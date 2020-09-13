from datetime import datetime


class Item:
    def __init__(self, item: dict):
        self.item = item

    @property
    def title(self):
        return self.item.get('title')

    @property
    def link(self):
        return self.item.get('link')

    @property
    def question_id(self):
        return self.item.get('question_id')

    @property
    def creation_date(self):
        creation_date = self.item.get('creation_date')
        return datetime.fromtimestamp(creation_date)


class SearchResponse:
    def __init__(self, response: dict):
        self.response = response

    @property
    def items(self):
        return [Item(item) for item in self.response.get('items')]

    @property
    def has_more(self):
        return self.response.get('has_more')

    @property
    def quota_max(self):
        return self.response.get('quota_max')

    @property
    def quota_remaining(self):
        return self.response.get('quota_remaining')

    @property
    def total(self):
        return self.response.get('total')
