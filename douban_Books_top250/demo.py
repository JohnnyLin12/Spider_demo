# -*- coding: utf-8 -*-
# @Time    : 2020/6/5 22:23
# @Author  : JohnnyLin
# @FileName: demo.py
# @Software: PyCharm

# 1、导入需要用到的库
import requests
from lxml import etree
import re  # 正则表达式
import csv

# 2、获取html代码（源码）
# 伪装成浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.61 Safari/537.36"
}


def get_onePage(url):
    response = requests.get(url, headers=headers, timeout=10)

    # 3、数据提取与处理

    # 将网页源码转为html对象
    html = etree.HTML(response.text)
    # 获得每本书的信息
    books = html.xpath('//tr[@class="item"] ')

    # 书籍引用语 注意第四页只有24条引语 海子的诗那本没有引语
    quote = []
    # 标签树
    # <tr class="item"> < td >
    # <p class="pl">[清] 曹雪芹 著 / 人民文学出版社 / 1996-12 / 59.70元</p>
    # <p class="quote" style="margin: 10px 0; color: #666"><span class="inq">都云作者痴，谁解其中味？</span></p>
    # </td></tr>
    for book in books:
        # <td>标签的第二个p标签
        quote_ = book.xpath('td/p[2]/span/text()')
        # quote_[0]提取列表里面的元素 除去[]
        quote.append(quote_[0] if len(quote_) != 0 else ' ')
    # print(quote)
    # 书名title在 <div class="pl2"> <a href="url" title="红楼梦">红楼梦  </div>
    # 返回列表
    books_name = html.xpath('//div[@class="pl2"]/a/@title')

    # 评分rating_nums  <span class="rating_nums">9.6</span>  text()方法输出该html标签的文本信息
    rating_nums = html.xpath('//span[@class="rating_nums"]/text()')

    # 评价人数  <span class="pl">( 286597人评价)</span>
    comment_persons = html.xpath('//span[@class="pl"]/text()')
    # 返回值是列表['(\n                    286603人评价\n                )', '(\n                    485043人评价\n  )'……]
    # 因此需要进行数据处理
    comment_personNums = []
    for i in comment_persons:
        comment_personNums.append(i.strip('()\n 人评价'))

    # 书作者 译者 出版社信息在<p class="pl">[清] 曹雪芹 著 / 人民文学出版社 / 1996-12 / 59.70元</p>

    books_info = html.xpath('//p[@class="pl"]/text()')

    # 处理书籍信息
    info = []
    author = []
    translator = []
    publisher = []
    publish_time = []
    price = []
    for i in books_info:
        info = i.split('/')
        author.append(info[0])
        # 翻译者这一列可能为空 要额外处理
        translator.append(info[1] if len(info) == 5 else " ")
        publisher.append(info[-3])
        publish_time.append(info[-2])
        price.append(info[-1])

    '''
        print(books_name)
        print(author)
        print(translator)
        print(rating_nums)
        print(comment_personNums)
        print(quote)
        print(publisher)
        print(publish_time)
    '''
    # 将每本书的信息按书名 作者 译者 星数 评价人数 引语 出版社 出版时间 价格 封装book_info列表
    books_data = []
    for i in range(25):
        books_data.append([books_name[i], author[i], translator[i],
                           rating_nums[i], comment_personNums[i], quote[i]
                              , publisher[i], publish_time[i], price[i]])

    return books_data


# 调用函数模块
# 集中在该if分支下调用函数 可以清楚地了解该程序的逻辑关系 是一种良好的编程习惯 程序结果与分散调用一样
if __name__ == "__main__":
    # 4、数据持久化
    with open('doubanBooks_top250.csv', 'w', encoding='utf-8', newline='') as f:
        # 通过csv模块获得writer对象 newline=''不加每行会有空行出现
        writer = csv.writer(f)
        # 整行写入
        writer.writerow(['书名', '作者', '译者', '星数', '评价人数', '引语', '出版社', '出版时间', '价格'])
        for i in range(10):
            link = "https://book.douban.com/top250?start=" + str(i * 25)
            print('页数：' + str(i + 1))
            for j in get_onePage(link):
                writer.writerow(j)

