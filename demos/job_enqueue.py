from jobs import app

if __name__ == '__main__':
    def enqueue_request(task_name: str, *args, **kwargs):
        """
        Enqueue a task to the Celery queue.

        :param task_name: The name of the task to enqueue (e.g., 'demos.jobs.hello').
        :param args: Positional arguments for the task.
        :param kwargs: Keyword arguments for the task.
        :return: The task result object.
        """
        _result = app.send_task(task_name, args=args, kwargs=kwargs)
        return _result


    # Enqueue the 'hello' task
    result = enqueue_request('demos.jobs.hello')

    # Check the task result
    print(f"Task ID: {result.id}")
    print(f"Task Status: {result.status}")
    print(result.get(timeout=10))