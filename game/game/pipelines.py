# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
"""
存储数据的方案：
    1、数据存储在csv文件中
    2、数据存储在mysql数据库中
    3、数据存储在MongoDB数据库中
    4、文件的存储
"""
import pymysql

class GamePipeline:
    def open_spider(self):
        self.f = open('./game.csv', 'a', encoding='utf-8', newline='')

    def close_spider(self):
        if self.f:
            self.f.close()

    def process_item(self, item, spider):
        self.f.write(f"{item['name']}, {item['category']}, {item['date']}\n")
        return item

# 管道默认不生效，需要去settings里面开启管道
class GameMySQLPipeline:
    def open_spider(self, spider):
        try:
            self.connection = pymysql.connect(
                host=spider.settings.get('MYSQL_HOST'),  # 数据库服务器地址
                user=spider.settings.get('MYSQL_USER'),  # 数据库用户名
                port=spider.settings.get('MYSQL_PORT'), #端口号
                password=spider.settings.get('MYSQL_PASSWORD'),  # 数据库密码
                database=spider.settings.get('MYSQL_NAME'),  # 要连接的数据库名
                charset='utf8mb4',  # 字符集，防止中文乱码
                cursorclass=pymysql.cursors.DictCursor  # 返回字典形式的结果，我个人觉得更方便
            )
            print("数据库连接成功！")

        except pymysql.Error as e:
            print(f"数据库连接失败: {e}")

    def close_spider(self, spider):
        # 8. 关闭连接
        # 无论成功失败，都确保关闭连接，释放资源
        if 'self.connection' in locals() and self.connection.open:
            self.connection.close()
            print("数据库连接已关闭。")

    # 5.执行数据插入操作
    @classmethod
    def insert_into(cls, item, cursor, table_name):
        insert_sql = f"INSERT INTO {table_name} (id, name, category, date) VALUES (null, %s, %s, %s)"
        game_data = (item['name'], item['category'], item['date'])
        cursor.execute(insert_sql, game_data)
        print(f"插入了一条数据，ID: {item['name']}")  # 获取最后插入的ID

    def process_item(self, item, spider):
        try:
            # 游标就像是你在数据库里操作的“光标”，所有的SQL命令都通过它来执行
            with (self.connection.cursor() as cursor):
                # 3. 执行SQL查询
                # sql_query = "SELECT *from students"
                # cursor.execute(sql_query)  # 参数化查询是好习惯，防止SQL注入
                table_name = spider.settings.get('MYSQL_SHEETNAME')
                # print(f"Table {table_name} exists.")
                self.insert_into(item, cursor, table_name)
                # 7. 提交事务
                # 对于INSERT, UPDATE, DELETE操作，需要提交才能真正写入数据库
                self.connection.commit()
                print("事务已提交。")
        except pymysql.Error as e:
            print(f"数据库操作失败: {e}")
            # 发生错误时，回滚事务，撤销所有未提交的更改
            self.connection.rollback()
            print("事务已回滚。")
            # if 'self.connection' in locals() and self.connection.open:
            #     self.connection.rollback()
            #     print("事务已回滚。")
        return item

# class NewsPipeline:
#     def process_item(self, item, spider):
#         item['title'] = "hello,world!"
#         return item