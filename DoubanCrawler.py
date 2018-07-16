import bs4
import expanddouban
import csv

def getMovieUrl(category, location):    #任务1 获取每个地区、每个类型页面的URL
    """
    return a string corresponding to the URL of douban movie lists given category and location.
    """
    url = "https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影,{},{}".format(category, location)  #根据url的规则输出各种选择后的url
    return url

def getHtml(category, location):    #任务2 获取电影页面 HTML
    html = expanddouban.getHtml(getMovieUrl(category, location), True)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup

class Movie:    #任务3 定义电影类
    def __init__(self, name, rate, location, category, info_link, cover_link):
        self.name = name
        self.rate = rate
        self.location = location
        self.category = category
        self.info_link = info_link
        self.cover_link = cover_link
    def output(self):
        #return "{},{},{},{},{},{}".format(self.name, self.rate, self.location, self.category, self.info_link, self.cover_link)
        return [self.name, self.rate, self.location, self.category, self.info_link, self.cover_link]    #输入一个列表，方便csv文件输出是，一个类别是一个单元格

def getMovie(category, location):   #任务4 获得豆瓣电影的信息
    """
    return a list of Movie objects with the given category and location.
    """
    movies = []
    for loc in location:
        soup = getHtml(category, loc)   #获取页面Html
        content_div = soup.find(id='content').find(class_='list-wp').find_all('a', recursive=False)
        for element in content_div:
            if element.find(class_='rate').string is None:  #douban中虽然筛选了9-10分，但结果里存在没评分的电影
                print("There is no rate for \"{}\"",format(element.find(class_='title').string))
                continue
            else:
                if float(element.find(class_='rate').string) >= 9:  #douban中虽然筛选了9-10分，但是实际还是有低于9分的电影出现在结果中，所以在程序中增加筛选
                    M_name = element.find(class_='title').string
                    M_rate = element.find(class_='rate').string
                    M_location = loc
                    M_category = category
                    M_info_link = element.get('href')
                    M_cover_link = element.find('img').get('src')
                    movies.append(Movie(M_name,M_rate,M_location,M_category,M_info_link,M_cover_link).output())
                else:
                    continue
    return movies

#任务5 构造电影信息数据表
douban_category = []    #准备获取豆瓣中包含的电影类型
douban_location = []    #准备获取豆瓣中包含的地区
html = expanddouban.getHtml("https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影", False, 0)
soup = bs4.BeautifulSoup(html, 'html.parser')
content_category = soup.find(id='content').find_all(class_='category')
#开始获取电影类型
category_lists = content_category[1]    #获得所有豆瓣中包含的电影类型（包含在html中第2个category中）
category_elements = category_lists.find_all('span')
for category_element in category_elements[1:]:  #历遍除了“所有类型”之外的所有电影类型
    douban_category.append(category_element.string)
#开始获取地区
location_lists = content_category[2]    #获得所有豆瓣中包含的地区（包含在html中第3个category中）
location_elements = location_lists.find_all('span')
for location_element in location_elements[1:]:
    douban_location.append(location_element.string)

category = ['剧情','爱情','动作']   #选择3个电影类型
location = douban_location  #选择豆瓣支持的所有地区
with open('movies.csv', 'w', newline='') as cf:
    for cate_choice in category:    #判断所选类型是否在豆瓣支持的类型列表中
        if cate_choice in douban_category:
            movie_list = getMovie(cate_choice, location)
            moviewriter = csv.writer(cf)
            for movie in movie_list:
                moviewriter.writerow(movie)
            continue
        else:
            print("Category: \"{}\" is not supported by Douban.com".format(cate_choice))

#任务6 统计电影数据
def add(location, dict):
    dict["sum"] += 1    #累加电影总数
    if location not in dict:    #累加各地区电影总数
        dict[location] = 1
    else:
        dict[location] += 1

with open('movies.csv', 'r') as f:
    reader = csv.reader(f)
    movie_datum = list(reader)
    output = open('output.txt', 'w')
    for cate in category:
        movie_dict = {"sum": 0} #创建一个字典，存放地区名和该地区电影数量以及该类型电影总数
        for movie_data in movie_datum:
            if movie_data[3] == cate:
                add(movie_data[2], movie_dict)
        top = sorted(movie_dict.items(), key=lambda x: x[1], reverse=True)  #按照电影数量进行排序
        loc_top_1 = None    #初始化前三位地区名和比例，防止该类型电影的地区不超过3个
        rate_top_1 = 0.0
        loc_top_2 = None
        rate_top_2 = 0.0
        loc_top_3 = None
        rate_top_3 = 0.0
        try:
            loc_top_1 = top[1][0]   #获取排名前三的地区名，并计算比例
            rate_top_1 = top[1][1]/top[0][1] * 100
            loc_top_2 = top[2][0]
            rate_top_2 = top[2][1]/top[0][1] * 100
            loc_top_3 = top[3][0]
            rate_top_3 = top[3][1]/top[0][1] * 100
        except:
            print("There're no 3 locations in category {}. \
Please refer to output.txt for more details".format(cate))
        finally:
            message = "Category: {}\n1st: {} {:0.2f}%\n2nd: {} {:0.2f}%\n3rd: {} {:0.2f}%\n\n"
            output.write(message.format(cate, loc_top_1, rate_top_1, loc_top_2, rate_top_2, loc_top_3, rate_top_3))
    output.close()
