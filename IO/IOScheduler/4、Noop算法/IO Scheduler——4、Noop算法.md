# IO Scheduler——4、Noop算法

Noop调度器的实现非常简单，其主要完成了一个`elevator request_queue`，这个`request_queue`没有进行任何的分类处理，只是对输入的request进行简单的队列操作。但是，需要注意的是，Noop基本上没有做什么特殊的事情，就是把邻近bio进行合并处理，从而最大限度的保证相邻的bio得到合并处理。Noop调度器实现了elevator的基本接口函数，并将这些函数注册到Linux系统的elevator子系统中。

需要注册到elevator子系统中的基本接口函数声明如下：

```c
static struct elevator_type elevator_noop = {
	.ops.sq = {
		.elevator_merge_req_fn		= noop_merged_requests,
		.elevator_dispatch_fn		= noop_dispatch,
		.elevator_add_req_fn		= noop_add_request,
		.elevator_former_req_fn		= noop_former_request,
		.elevator_latter_req_fn		= noop_latter_request,
		.elevator_init_fn		= noop_init_queue,
		.elevator_exit_fn		= noop_exit_queue,
	},
	.elevator_name = "noop",
	.elevator_owner = THIS_MODULE,
};
```

| 接口函数             | 说明                              |
| -------------------- | --------------------------------- |
| noop_merged_requests | 合并两个request                   |
| noop_dispatch        | 调度一个合适的request进行发送处理 |
| noop_add_request     | 将request放入调度器的queue中      |
| noop_format_request  | 获取前一个request                 |
| noop_latter_request  | 获取后一个request                 |

由于Noop调度器没有对`request`进行任何的分类处理、调度，因此上述这些函数的实现都很简单。

## noop_dispatch

当调度器需要发送`request`时，会调用`noop_dispatch`。该函数会直接从调度器所管理的`request_queue`中获取一个`request`，然后调用`elv_dispatch_sort`函数将请求加入到设备所在的`request_queue`中。`noop_dispatch`函数实现如下：

```c
static int noop_dispatch(struct request_queue *q, int force)
{
	struct noop_data *nd = q->elevator->elevator_data;
	struct request *rq;

	rq = list_first_entry_or_null(&nd->queue, struct request, queuelist);
	if (rq) {
		list_del_init(&rq->queuelist);
		elv_dispatch_sort(q, rq);
		return 1;
	}
	return 0;
}
```

## noop_add_request

当需要往noop调度器中放入`request`时，可以调用`noop_add_request`，该函数的实现及其简单，就是将`request`挂入调度器所维护的`request_queue`中，`noop_add_request`函数实现如下：

```c
static void noop_add_request(struct request_queue *q, struct request *rq)
{
	struct noop_data *nd = q->elevator->elevator_data;

	list_add_tail(&rq->queuelist, &nd->queue);
}
```



由此可见，noop调度器的实现是很简单的，仅仅实现了一个调度器的框架，用一条链表把所有输入的`request`管理起来。