# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql

# 管道默认不生效，需要去settings里面开启管道
class GamePipeline:
    # 判断数据表是否存在
    @classmethod
    def table_exists(cls, table_name, cursor):
        query = f"SHOW TABLES LIKE '{table_name}'"
        cursor.execute(query)
        result = cursor.fetchone()
        return result is not None

    # 5.执行数据插入操作
    @classmethod
    def insert_into(cls, item, cursor, table_name):
        insert_sql = f"INSERT INTO {table_name} (id, name, category, date) VALUES (null, %s, %s, %s)"
        game_data = (item['name'], item['category'], item['date'])
        cursor.execute(insert_sql, game_data)
        print(f"插入了一条数据，ID: {item['name']}")  # 获取最后插入的ID

    def process_item(self, item, spider):
        # 1. 建立连接
        # 数据库信息
        # 我通常会把这些敏感信息放在环境变量或者配置文件里，避免硬编码
        try:
            connection = pymysql.connect(
                host=spider.settings.get('MYSQL_HOST'),  # 数据库服务器地址
                user=spider.settings.get('MYSQL_USER'),  # 数据库用户名
                password=spider.settings.get('MYSQL_PASSWORD'),  # 数据库密码
                database=spider.settings.get('MYSQL_NAME'),  # 要连接的数据库名
                charset='utf8mb4',  # 字符集，防止中文乱码
                cursorclass=pymysql.cursors.DictCursor  # 返回字典形式的结果，我个人觉得更方便
            )
            print("数据库连接成功！")

            # 2. 创建游标对象
            # 游标就像是你在数据库里操作的“光标”，所有的SQL命令都通过它来执行
            with connection.cursor() as cursor:
                # 3. 执行SQL查询
                # sql_query = "SELECT *from students"
                # cursor.execute(sql_query)  # 参数化查询是好习惯，防止SQL注入
                table_name = spider.settings.get('MYSQL_SHEETNAME')
                if self.table_exists(table_name, cursor):
                    # print(f"Table {table_name} exists.")
                    self.insert_into(item, cursor, table_name)
                else:
                    print(f"Table {table_name} does not exist.")

                # 7. 提交事务
                # 对于INSERT, UPDATE, DELETE操作，需要提交才能真正写入数据库
                connection.commit()
                print("事务已提交。")

        except pymysql.Error as e:
            print(f"数据库操作失败: {e}")
            # 发生错误时，回滚事务，撤销所有未提交的更改
            if 'connection' in locals() and connection.open:
                connection.rollback()
                print("事务已回滚。")
        finally:
            # 8. 关闭连接
            # 无论成功失败，都确保关闭连接，释放资源
            if 'connection' in locals() and connection.open:
                connection.close()
                print("数据库连接已关闭。")
        return item

# class NewsPipeline:
#     def process_item(self, item, spider):
#         item['title'] = "hello,world!"
#         return item