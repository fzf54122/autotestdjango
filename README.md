1. celery任务同步
2. 任务结果异步存储处理，通过一个定时任务进行处理，避免每个任务都要进行数据库访问
3. 和ones工单id关联
4. 解决depends_on和list_data混用时的函数签名异常
5. 在unittest.TestCase上添加tags，并实现将版本管理通过tags实现，避免目录中出现'.'这种敏感符号
6. 随即数据生成和jsonpath提取目前的调用方式比较麻烦，考虑优化方式，通过组合的方式提供给TestCase类
7. history数据考虑放在数据库中进行处理（或者缓存）