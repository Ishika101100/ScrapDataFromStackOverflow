import scrapy
import csv

from ..items import StackoverflowItem


class Stack(scrapy.Spider):
    """
    class stack is used to run spider named stackoverflow
    """
    name = 'stackoverflow'

    def start_requests(self):
        """
        Spider will begin to crawl stackoverflow website from the given input tag
        :return: request data from stackoverflow of the provided url
        """
        with open('tags.csv', 'r') as file_data:
            dict_reader = csv.reader(file_data)
            list_of_dict = list(dict_reader)
            final_tags=[]
            for i in range(len(list_of_dict)):
                final_tags.append(list_of_dict[i][0])
            tag_input = input("Enter tag name :")
            if tag_input in final_tags:
                try:
                    page_input = int(input("Enter number of page :"))
                    for url in range(page_input):
                        urls = f'https://stackoverflow.com/questions/tagged/{tag_input}?tab=Frequent&page={url + 1}&pagesize=50'
                        yield scrapy.Request(url=urls, callback=self.parse)
                except ValueError:
                    print('invalid_input')
            else:
                print(f"There is no such a tag like -----'{tag_input}'")
                return self.start_requests

    def parse(self, response):
        """
        question details data is scrapped in this function
        :param response: accepts response from the stackoverflow website
        :return: if answer count for a question is greater than 0 then request data from answer's link else return none
        """
        questions = '.s-post-summary'
        for q in response.css(questions):
            stack_question_id = q.css(
                "div.s-post-summary--content h3.s-post-summary--content-title a.s-link::attr(href)").extract_first().split(
                "/")[2]
            question_title = q.css(
                "div.s-post-summary--content h3.s-post-summary--content-title a.s-link::text").extract_first()

            question_content = q.css(
                "div.s-post-summary--content div.s-post-summary--content-excerpt::text").extract_first().strip('/r/n ')
            question_url = q.css(
                "div.s-post-summary--content h3.s-post-summary--content-title a.s-link::attr(href)").extract_first()
            date_posted = q.css(
                "div.s-post-summary--content div.s-post-summary--meta div.s-user-card time.s-user-card--time span.relativetime::text").extract_first()
            upvote = q.css(
                '.s-post-summary--stats .s-post-summary--stats-item .s-post-summary--stats-item-number::text').extract()[
                0]
            view = q.css(
                '.s-post-summary--stats .s-post-summary--stats-item .s-post-summary--stats-item-number::text').extract()[
                2]
            tags = q.css(
                'div.s-post-summary--content div.s-post-summary--meta div.s-post-summary--meta-tags a::text').extract()
            answers_count = q.css(
                '.s-post-summary--stats .s-post-summary--stats-item .s-post-summary--stats-item-number::text').extract()[
                1]
            stack_user_id = q.css(
                'div.s-post-summary--content div.s-post-summary--meta div.s-user-card a.s-avatar div.gravatar-wrapper-16::attr(data-user-id)').extract_first()
            user_name = q.css(
                'div.s-post-summary--content div.s-post-summary--meta div.s-user-card div.s-user-card--info div.s-user-card--link a.flex--item::text').extract_first()

            user_reputation_score = q.css(
                "div.s-post-summary--content div.s-post-summary--meta div.s-user-card div.s-user-card--info ul.s-user-card--awards li.s-user-card--rep span.todo-no-class-here::text").extract()

            user = {
                'stack_user_id': stack_user_id,
                'name': user_name,
                'reputation_score': (user_reputation_score[0]) if len(user_reputation_score) > 0 else 0
            }

            stackoverflow = {
                'stack_question_id': stack_question_id,
                'question_title': question_title,
                'question_content': question_content,
                'question_url': question_url,
                'date_posted': date_posted,
                'upvote': (upvote[0]),
                'view': (view[0]),
                'tags': tags,
                'answers_count': (answers_count[0]),
                'user': user,
                'answers': []
            }

            if int(answers_count[0]) >= 0:
                yield response.follow('https://stackoverflow.com' + question_url, self.parse_answer,
                                      meta={'stackoverflow': stackoverflow})

    def parse_answer(self, response):
        """
        if no of answers in a particular question is greater than one then this function will be scrap answer details
        for the respective question
        :param response: collect responses from parse function
        :return: item in which question and answer data is stored
        """
        item = StackoverflowItem()
        stackoverflow = response.meta['stackoverflow']

        questionComments = response.css('#question .js-comment')
        q_comments = []
        for qc in questionComments:
            stack_question_comment_id = qc.css('.js-comment::attr(data-comment-id)').extract_first()
            comment_content = qc.css('.comment-copy::text').extract()
            try:
                user_id = qc.css('.comment-user::attr(href)').extract()
            except Exception:
                user_id = None

            comment = {
                'stack_question_id': stackoverflow['stack_question_id'],
                'stack_question_comment_id': stack_question_comment_id,
                'comment_content': comment_content[0] if len(comment_content) > 0 else ' ',
                'user_id': user_id[0].split("/")[2]
            }

            q_comments.append(comment)

        answers = stackoverflow['answers']
        anss = response.css('.answer')
        for a in anss:
            stack_answer_id = a.css('.answer::attr(id)').extract_first().split("-")[1]
            answer_content = a.css('.js-post-body *::text').getall()
            date_posted = a.css('.relativetime::attr(title)').extract()
            upvote = a.css('.fs-title::text').extract()
            accepted = a.css('div.d-none::attr(title)').get(default='Accepted')
            try:
                stack_user_id = a.css('.user-details a::attr(href)').extract_first().split("/")[2]
            except Exception:
                stack_user_id = None

            user_name = a.css('.user-details a::text').extract()
            user_reputation_score = a.css('.reputation-score::text').extract()

            user = {
                'stack_user_id': stack_user_id,
                'name': user_name[0],
                'reputation_score': (user_reputation_score[0]) if len(user_reputation_score) > 0 else 0
            }
            answerComments = a.css('.js-comment')
            a_comments = []
            for ac in answerComments:
                stack_answer_comment_id = ac.css('.js-comment::attr(data-comment-id)').extract_first()
                comment_content = ac.css('.comment-copy::text').extract()
                try:
                    user_id = ac.css('.comment-user::attr(href)').extract()
                except Exception:
                    user_id = None

                comment = {
                    'stack_answer_id': stack_answer_id,
                    'stack_answer_comment_id': stack_answer_comment_id,
                    'comment_content': comment_content[0] if len(comment_content) > 0 else ' ',
                    'user_id': user_id[0].split("/")[2]
                }

                a_comments.append(comment)
            answer = {
                'stack_answer_id': stack_answer_id,
                'answer_content': " ".join(answer_content),
                'date_posted': date_posted[0],
                'upvote': (upvote[0]),
                'accepted': "Yes" if "Accepted" in accepted else "No",
                'user': user,
                'answer_comments': a_comments
            }

            answers.append(answer)

        stackoverflow['answers'] = answers
        stackoverflow['question_comments'] = q_comments
        item['stack_question_id'] = stackoverflow['stack_question_id']
        item['question_title'] = stackoverflow['question_title']
        item['question_content'] = stackoverflow['question_content']
        item['question_url'] = stackoverflow['question_url']
        item['date_posted'] = stackoverflow['date_posted']
        item['upvote'] = stackoverflow['upvote']
        item['view'] = stackoverflow['view']
        item['tags'] = stackoverflow['tags']
        item['answers_count'] = stackoverflow['answers_count']
        item['answers'] = stackoverflow['answers']
        item['user'] = stackoverflow['user']
        item['question_comments'] = stackoverflow['question_comments']

        yield item
