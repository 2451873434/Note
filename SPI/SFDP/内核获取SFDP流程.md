# 内核获取`SFDP`流程

> drivers/mtd/spi-nor/sfdp.c



## `spi_nor_parse_sfdp()`

```c
/**
 * spi_nor_parse_sfdp() - parse the Serial Flash Discoverable Parameters.
 * @nor:		pointer to a 'struct spi_nor'
 *
 * The Serial Flash Discoverable Parameters are described by the JEDEC JESD216
 * specification. This is a standard which tends to supported by almost all
 * (Q)SPI memory manufacturers. Those hard-coded tables allow us to learn at
 * runtime the main parameters needed to perform basic SPI flash operations such
 * as Fast Read, Page Program or Sector Erase commands.
 *
 * Return: 0 on success, -errno otherwise.
 */
int spi_nor_parse_sfdp(struct spi_nor *nor)
{
	const struct sfdp_parameter_header *param_header, *bfpt_header;
	struct sfdp_parameter_header *param_headers = NULL;
	struct sfdp_header header;
	struct device *dev = nor->dev;
	struct sfdp *sfdp;
	size_t sfdp_size;
	size_t psize;
	int i, err;

	/* Get the SFDP header. */
    /* 读取SFDP的前16个字节，即u32[0-3] */
	err = spi_nor_read_sfdp_dma_unsafe(nor, 0, sizeof(header), &header);
	if (err < 0)
		return err;

	/* Check the SFDP header version. */
    /* 校验SFDP表名字（00-03h）及主版本号（05h） */
	if (le32_to_cpu(header.signature) != SFDP_SIGNATURE ||
	    header.major != SFDP_JESD216_MAJOR)
		return -EINVAL;

	/*
	 * Verify that the first and only mandatory parameter header is a
	 * Basic Flash Parameter Table header as specified in JESD216.
	 */
    /* 校验BFPT ID（0fh和08h）和主版本号（0ah） */
	bfpt_header = &header.bfpt_header;
	if (SFDP_PARAM_HEADER_ID(bfpt_header) != SFDP_BFPT_ID ||
	    bfpt_header->major != SFDP_JESD216_MAJOR)
		return -EINVAL;

    /* 
     * 计算SFDP大小，前者是BFPT起始地址偏移（0c-0eh），值一般为000030h，后者
     * 为BFPT大小，单位为double word，即4字节。有些flash有其自定义的PT表，所
     * 这只是初步计算SFDP大小，后续肯定会加上自定义表大小。
     */
	sfdp_size = SFDP_PARAM_HEADER_PTP(bfpt_header) +
		    SFDP_PARAM_HEADER_PARAM_LEN(bfpt_header);

	/*
	 * Allocate memory then read all parameter headers with a single
	 * Read SFDP command. These parameter headers will actually be parsed
	 * twice: a first time to get the latest revision of the basic flash
	 * parameter table, then a second time to handle the supported optional
	 * tables.
	 * Hence we read the parameter headers once for all to reduce the
	 * processing time. Also we use kmalloc() instead of devm_kmalloc()
	 * because we don't need to keep these parameter headers: the allocated
	 * memory is always released with kfree() before exiting this function.
	 */
    /* 
     * 判断是否有自定义PT表，然后读取所有的自定义PT表，并将数据放在param_headers中。
     */
	if (header.nph) {
		psize = header.nph * sizeof(*param_headers);

		param_headers = kmalloc(psize, GFP_KERNEL);
		if (!param_headers)
			return -ENOMEM;

		err = spi_nor_read_sfdp(nor, sizeof(header),
					psize, param_headers);
		if (err < 0) {
			dev_dbg(dev, "failed to read SFDP parameter headers\n");
			goto exit;
		}
	}

	/*
	 * Cache the complete SFDP data. It is not (easily) possible to fetch
	 * SFDP after probe time and we need it for the sysfs access.
	 */
    /* 
     * 遍历所有自定义PT表，计算SFDP大小。一般来说自定义表是依次放在BFPT表后，且PTP依
     * 次增大，所以一般情况下SFDP大小为最后一个自定义PT表的PTP加上其LEN。
     */
	for (i = 0; i < header.nph; i++) {
		param_header = &param_headers[i];
		sfdp_size = max_t(size_t, sfdp_size,
				  SFDP_PARAM_HEADER_PTP(param_header) +
				  SFDP_PARAM_HEADER_PARAM_LEN(param_header));
	}

	/*
	 * Limit the total size to a reasonable value to avoid allocating too
	 * much memory just of because the flash returned some insane values.
	 */
	if (sfdp_size > PAGE_SIZE) {
		dev_dbg(dev, "SFDP data (%zu) too big, truncating\n",
			sfdp_size);
		sfdp_size = PAGE_SIZE;
	}

	sfdp = devm_kzalloc(dev, sizeof(*sfdp), GFP_KERNEL);
	if (!sfdp) {
		err = -ENOMEM;
		goto exit;
	}

	/*
	 * The SFDP is organized in chunks of DWORDs. Thus, in theory, the
	 * sfdp_size should be a multiple of DWORDs. But in case a flash
	 * is not spec compliant, make sure that we have enough space to store
	 * the complete SFDP data.
	 */
    /* 计算SFDP表有多少个double word，即有多少个4字节 */
	sfdp->num_dwords = DIV_ROUND_UP(sfdp_size, sizeof(*sfdp->dwords));
	sfdp->dwords = devm_kcalloc(dev, sfdp->num_dwords,
				    sizeof(*sfdp->dwords), GFP_KERNEL);
	if (!sfdp->dwords) {
		err = -ENOMEM;
		devm_kfree(dev, sfdp);
		goto exit;
	}

    /* 读取SFDP所有数据，并存放在sfdp->dwords中 */
	err = spi_nor_read_sfdp(nor, 0, sfdp_size, sfdp->dwords);
	if (err < 0) {
		dev_dbg(dev, "failed to read SFDP data\n");
		devm_kfree(dev, sfdp->dwords);
		devm_kfree(dev, sfdp);
		goto exit;
	}

	nor->sfdp = sfdp;

	/*
	 * Check other parameter headers to get the latest revision of
	 * the basic flash parameter table.
	 */
    /*
     * 自定义PT表中可能有BFPT表，这时之前的BFPT表可能就不是最新版本的。所以
     * 遍历每一个自定义PT表，然后通过ID识别BFPT表，再筛选出最新版本的BFPT表。
     * 不过一般情况下只有一个BFPT表，并且该表紧挨着SFDP Header，BFPT表头所
     * 在位置（08-0fh），BFPT表所在位置（30h-xxh）。
     */
	for (i = 0; i < header.nph; i++) {
		param_header = &param_headers[i];

		if (SFDP_PARAM_HEADER_ID(param_header) == SFDP_BFPT_ID &&
		    param_header->major == SFDP_JESD216_MAJOR &&
		    (param_header->minor > bfpt_header->minor ||
		     (param_header->minor == bfpt_header->minor &&
		      param_header->length > bfpt_header->length)))
			bfpt_header = param_header;
	}

    /* 解析BFPT表 */
	err = spi_nor_parse_bfpt(nor, bfpt_header);
	if (err)
		goto exit;

	/* Parse optional parameter tables. */
    /* 解析其他自定义的PT表 */
	for (i = 0; i < header.nph; i++) {
		param_header = &param_headers[i];

		switch (SFDP_PARAM_HEADER_ID(param_header)) {
		case SFDP_SECTOR_MAP_ID:
			err = spi_nor_parse_smpt(nor, param_header);
			break;

		case SFDP_4BAIT_ID:
			err = spi_nor_parse_4bait(nor, param_header);
			break;

		case SFDP_PROFILE1_ID:
			err = spi_nor_parse_profile1(nor, param_header);
			break;

		case SFDP_SCCR_MAP_ID:
			err = spi_nor_parse_sccr(nor, param_header);
			break;

		case SFDP_SCCR_MAP_MC_ID:
			err = spi_nor_parse_sccr_mc(nor, param_header);
			break;

		default:
			break;
		}

		if (err) {
			dev_warn(dev, "Failed to parse optional parameter table: %04x\n",
				 SFDP_PARAM_HEADER_ID(param_header));
			/*
			 * Let's not drop all information we extracted so far
			 * if optional table parsers fail. In case of failing,
			 * each optional parser is responsible to roll back to
			 * the previously known spi_nor data.
			 */
			err = 0;
		}
	}

	err = spi_nor_post_sfdp_fixups(nor);
exit:
	kfree(param_headers);
	return err;
}
```

## `spi_nor_read_sfdp_dma_unsafe()`

```c
/**
 * spi_nor_read_sfdp_dma_unsafe() - read Serial Flash Discoverable Parameters.
 * @nor:	pointer to a 'struct spi_nor'
 * @addr:	offset in the SFDP area to start reading data from
 * @len:	number of bytes to read
 * @buf:	buffer where the SFDP data are copied into
 *
 * Wrap spi_nor_read_sfdp() using a kmalloc'ed bounce buffer as @buf is now not
 * guaranteed to be dma-safe.
 *
 * Return: -ENOMEM if kmalloc() fails, the return code of spi_nor_read_sfdp()
 *          otherwise.
 */
static int spi_nor_read_sfdp_dma_unsafe(struct spi_nor *nor, u32 addr,
					size_t len, void *buf)
{
	void *dma_safe_buf;
	int ret;

	dma_safe_buf = kmalloc(len, GFP_KERNEL);
	if (!dma_safe_buf)
		return -ENOMEM;

	ret = spi_nor_read_sfdp(nor, addr, len, dma_safe_buf);
	memcpy(buf, dma_safe_buf, len);
	kfree(dma_safe_buf);

	return ret;
}
```

## `spi_nor_read_sfdp()`

```c
/**
 * spi_nor_read_sfdp() - read Serial Flash Discoverable Parameters.
 * @nor:	pointer to a 'struct spi_nor'
 * @addr:	offset in the SFDP area to start reading data from
 * @len:	number of bytes to read
 * @buf:	buffer where the SFDP data are copied into (dma-safe memory)
 *
 * Whatever the actual numbers of bytes for address and dummy cycles are
 * for (Fast) Read commands, the Read SFDP (5Ah) instruction is always
 * followed by a 3-byte address and 8 dummy clock cycles.
 *
 * Return: 0 on success, -errno otherwise.
 */
static int spi_nor_read_sfdp(struct spi_nor *nor, u32 addr,
			     size_t len, void *buf)
{
	u8 addr_nbytes, read_opcode, read_dummy;
	int ret;

    /*
     * 读SFDP需要发送0x5a指令，所以会对read_opcode、addr_nbytes、read_dummy做修
     * 改，因此需要保存之前的值
     */
	read_opcode = nor->read_opcode;
	addr_nbytes = nor->addr_nbytes;
	read_dummy = nor->read_dummy;

	nor->read_opcode = SPINOR_OP_RDSFDP;
	nor->addr_nbytes = 3;
	nor->read_dummy = 8;

	ret = spi_nor_read_raw(nor, addr, len, buf);

    /* 读取完SFDP后恢复之前的值 */
	nor->read_opcode = read_opcode;
	nor->addr_nbytes = addr_nbytes;
	nor->read_dummy = read_dummy;

	return ret;
}
```

## `spi_nor_parse_bfpt()`

```c
static int spi_nor_parse_bfpt(struct spi_nor *nor,
			      const struct sfdp_parameter_header *bfpt_header)
{
	struct spi_nor_flash_parameter *params = nor->params;
	struct spi_nor_erase_map *map = &params->erase_map;
	struct spi_nor_erase_type *erase_type = map->erase_type;
	struct sfdp_bfpt bfpt;
	size_t len;
	int i, cmd, err;
	u32 addr, val;
	u32 dword;
	u16 half;
	u8 erase_mask;

	/* JESD216 Basic Flash Parameter Table length is at least 9 DWORDs. */
    /* 216版本的BFPT表长度至少为9个double word，即36字节 */
	if (bfpt_header->length < BFPT_DWORD_MAX_JESD216)
		return -EINVAL;

	/* Read the Basic Flash Parameter Table. */
    /* 计算SFPT表的长度（0bh）和地址（0c-0eh） */
	len = min_t(size_t, sizeof(bfpt),
		    bfpt_header->length * sizeof(u32));
	addr = SFDP_PARAM_HEADER_PTP(bfpt_header);
	memset(&bfpt, 0, sizeof(bfpt));
    /* 读取BFPT表数据，并保存在bfpt中 */
	err = spi_nor_read_sfdp_dma_unsafe(nor,  addr, len, &bfpt);
	if (err < 0)
		return err;

	/* Fix endianness of the BFPT DWORDs. */
	le32_to_cpu_array(bfpt.dwords, BFPT_DWORD_MAX);

    /* 由于BFPT表有其标准协议，以下为对BFPT表数据进行解析 */
    
	/* Number of address bytes. */
    /* bfpt.dwords[SFDP_DWORD(1)]即30h-33h，bit[18:17]表示flash所支持的地址字节数 */
	switch (bfpt.dwords[SFDP_DWORD(1)] & BFPT_DWORD1_ADDRESS_BYTES_MASK) {
	case BFPT_DWORD1_ADDRESS_BYTES_3_ONLY:
	case BFPT_DWORD1_ADDRESS_BYTES_3_OR_4:
		params->addr_nbytes = 3;
		params->addr_mode_nbytes = 3;
		break;

	case BFPT_DWORD1_ADDRESS_BYTES_4_ONLY:
		params->addr_nbytes = 4;
		params->addr_mode_nbytes = 4;
		break;

	default:
		break;
	}

	/* Flash Memory Density (in bits). */
    /* bfpt.dwords[SFDP_DWORD(2)]即34h-37h，表示flash的大小，单位为bit */
	val = bfpt.dwords[SFDP_DWORD(2)];
	if (val & BIT(31)) {
		val &= ~BIT(31);

		/*
		 * Prevent overflows on params->size. Anyway, a NOR of 2^64
		 * bits is unlikely to exist so this error probably means
		 * the BFPT we are reading is corrupted/wrong.
		 */
		if (val > 63)
			return -EINVAL;

		params->size = 1ULL << val;
	} else {
		params->size = val + 1;
	}
	params->size >>= 3; /* Convert to bytes. */

	/* Fast Read settings. */
	for (i = 0; i < ARRAY_SIZE(sfdp_bfpt_reads); i++) {
		const struct sfdp_bfpt_read *rd = &sfdp_bfpt_reads[i];
		struct spi_nor_read_command *read;

		if (!(bfpt.dwords[rd->supported_dword] & rd->supported_bit)) {
			params->hwcaps.mask &= ~rd->hwcaps;
			continue;
		}

		params->hwcaps.mask |= rd->hwcaps;
		cmd = spi_nor_hwcaps_read2cmd(rd->hwcaps);
		read = &params->reads[cmd];
		half = bfpt.dwords[rd->settings_dword] >> rd->settings_shift;
		spi_nor_set_read_settings_from_bfpt(read, half, rd->proto);
	}

	/*
	 * Sector Erase settings. Reinitialize the uniform erase map using the
	 * Erase Types defined in the bfpt table.
	 */
	erase_mask = 0;
	memset(&params->erase_map, 0, sizeof(params->erase_map));
	for (i = 0; i < ARRAY_SIZE(sfdp_bfpt_erases); i++) {
		const struct sfdp_bfpt_erase *er = &sfdp_bfpt_erases[i];
		u32 erasesize;
		u8 opcode;

		half = bfpt.dwords[er->dword] >> er->shift;
		erasesize = half & 0xff;

		/* erasesize == 0 means this Erase Type is not supported. */
		if (!erasesize)
			continue;

		erasesize = 1U << erasesize;
		opcode = (half >> 8) & 0xff;
		erase_mask |= BIT(i);
		spi_nor_set_erase_settings_from_bfpt(&erase_type[i], erasesize,
						     opcode, i);
	}
	spi_nor_init_uniform_erase_map(map, erase_mask, params->size);
	/*
	 * Sort all the map's Erase Types in ascending order with the smallest
	 * erase size being the first member in the erase_type array.
	 */
	sort(erase_type, SNOR_ERASE_TYPE_MAX, sizeof(erase_type[0]),
	     spi_nor_map_cmp_erase_type, NULL);
	/*
	 * Sort the erase types in the uniform region in order to update the
	 * uniform_erase_type bitmask. The bitmask will be used later on when
	 * selecting the uniform erase.
	 */
	spi_nor_regions_sort_erase_types(map);
	map->uniform_erase_type = map->uniform_region.offset &
				  SNOR_ERASE_TYPE_MASK;

	/* Stop here if not JESD216 rev A or later. */
	if (bfpt_header->length == BFPT_DWORD_MAX_JESD216)
		return spi_nor_post_bfpt_fixups(nor, bfpt_header, &bfpt);

	/* Page size: this field specifies 'N' so the page size = 2^N bytes. */
	val = bfpt.dwords[SFDP_DWORD(11)];
	val &= BFPT_DWORD11_PAGE_SIZE_MASK;
	val >>= BFPT_DWORD11_PAGE_SIZE_SHIFT;
	params->page_size = 1U << val;

	/* Quad Enable Requirements. */
	switch (bfpt.dwords[SFDP_DWORD(15)] & BFPT_DWORD15_QER_MASK) {
	case BFPT_DWORD15_QER_NONE:
		params->quad_enable = NULL;
		break;

	case BFPT_DWORD15_QER_SR2_BIT1_BUGGY:
		/*
		 * Writing only one byte to the Status Register has the
		 * side-effect of clearing Status Register 2.
		 */
	case BFPT_DWORD15_QER_SR2_BIT1_NO_RD:
		/*
		 * Read Configuration Register (35h) instruction is not
		 * supported.
		 */
		nor->flags |= SNOR_F_HAS_16BIT_SR | SNOR_F_NO_READ_CR;
		params->quad_enable = spi_nor_sr2_bit1_quad_enable;
		break;

	case BFPT_DWORD15_QER_SR1_BIT6:
		nor->flags &= ~SNOR_F_HAS_16BIT_SR;
		params->quad_enable = spi_nor_sr1_bit6_quad_enable;
		break;

	case BFPT_DWORD15_QER_SR2_BIT7:
		nor->flags &= ~SNOR_F_HAS_16BIT_SR;
		params->quad_enable = spi_nor_sr2_bit7_quad_enable;
		break;

	case BFPT_DWORD15_QER_SR2_BIT1:
		/*
		 * JESD216 rev B or later does not specify if writing only one
		 * byte to the Status Register clears or not the Status
		 * Register 2, so let's be cautious and keep the default
		 * assumption of a 16-bit Write Status (01h) command.
		 */
		nor->flags |= SNOR_F_HAS_16BIT_SR;

		params->quad_enable = spi_nor_sr2_bit1_quad_enable;
		break;

	default:
		dev_dbg(nor->dev, "BFPT QER reserved value used\n");
		break;
	}

	dword = bfpt.dwords[SFDP_DWORD(16)] & BFPT_DWORD16_4B_ADDR_MODE_MASK;
	if (SFDP_MASK_CHECK(dword, BFPT_DWORD16_4B_ADDR_MODE_BRWR))
		params->set_4byte_addr_mode = spi_nor_set_4byte_addr_mode_brwr;
	else if (SFDP_MASK_CHECK(dword, BFPT_DWORD16_4B_ADDR_MODE_WREN_EN4B_EX4B))
		params->set_4byte_addr_mode = spi_nor_set_4byte_addr_mode_wren_en4b_ex4b;
	else if (SFDP_MASK_CHECK(dword, BFPT_DWORD16_4B_ADDR_MODE_EN4B_EX4B))
		params->set_4byte_addr_mode = spi_nor_set_4byte_addr_mode_en4b_ex4b;
	else
		dev_dbg(nor->dev, "BFPT: 4-Byte Address Mode method is not recognized or not implemented\n");

	/* Soft Reset support. */
	if (bfpt.dwords[SFDP_DWORD(16)] & BFPT_DWORD16_SWRST_EN_RST)
		nor->flags |= SNOR_F_SOFT_RESET;

	/* Stop here if not JESD216 rev C or later. */
	if (bfpt_header->length == BFPT_DWORD_MAX_JESD216B)
		return spi_nor_post_bfpt_fixups(nor, bfpt_header, &bfpt);

	/* 8D-8D-8D command extension. */
	switch (bfpt.dwords[SFDP_DWORD(18)] & BFPT_DWORD18_CMD_EXT_MASK) {
	case BFPT_DWORD18_CMD_EXT_REP:
		nor->cmd_ext_type = SPI_NOR_EXT_REPEAT;
		break;

	case BFPT_DWORD18_CMD_EXT_INV:
		nor->cmd_ext_type = SPI_NOR_EXT_INVERT;
		break;

	case BFPT_DWORD18_CMD_EXT_RES:
		dev_dbg(nor->dev, "Reserved command extension used\n");
		break;

	case BFPT_DWORD18_CMD_EXT_16B:
		dev_dbg(nor->dev, "16-bit opcodes not supported\n");
		return -EOPNOTSUPP;
	}

	return spi_nor_post_bfpt_fixups(nor, bfpt_header, &bfpt);
}
```

