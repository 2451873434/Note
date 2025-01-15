#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>

#define BEEPOFF	0
#define BEEPON 	1

/*
 * @description		: main主程序
 * @param - argc 	: argv数组元素个数
 * @param - argv 	: 具体参数
 * @return 			: 0 成功;其他 失败
 */
int main(int argc, char *argv[])
{
	int fd, retvalue;
	char *filename;
	unsigned char databuf[5];
	
	if(argc != 2){
		printf("Error Usage!\r\n");
		return -1;
	}

	filename = argv[1];
	fd = open(filename, O_RDWR);	/* 打开beep驱动 */
	if(fd < 0){
		printf("file %s open failed!\r\n", argv[1]);
		return -1;
	}

	printf("before read\n");
	read(fd, databuf, sizeof(databuf));
	printf("end read\n");

	for (int i = 0; i < 5; i++)
		printf("databuf[%d]=0x%x\n", i, databuf[i]);

	retvalue = close(fd); /* 关闭文件 */
	if(retvalue < 0){
		printf("file %s close failed!\r\n", argv[1]);
		return -1;
	}
	return 0;
}
