import typing

from elasticsearch import Elasticsearch


class Connection:
    def __init__(self, **info):
        self.client = Elasticsearch(**info)
    
    def get_default_keywords(
        self,
        index: str = 'information',
        doc_type: str = 'namugrim',
        size: int = 1024,
    ) -> typing.List[str]:
        keywords = self.client.search(index=index, doc_type=doc_type, size=size)
        
        return keywords['hits']['hits']

    def get_keywords(
        self,
        index: str = 'information',
        doc_type: str = 'namugrim',
        scroll: str = '1m',
        size: int = 1024
    ) -> typing.List[str]:

        def _get_scroll_(scroll):
            scroll_doc = scroll['hits']['hits']
            return len(scroll_doc), scroll_doc

        keywords = []
        scroll = self.client.search(index='information', doc_type='namugrim', scroll=scroll, size=size)
        scroll_id = scroll['_scroll_id']
        scrolled, scroll_doc = _get_scroll_(scroll)
        keywords.extend(scroll_doc)

        while scrolled:
            scroll = self.client.scroll(scroll_id=scroll_id, scroll='1m')
            scrolled, scroll_doc = _get_scroll_(scroll)
            keywords.extend(scroll_doc)
    
        return keywords

    def put_data(self, info: typing.Dict[str, typing.Any], index='information', doc_type='namugrim'):
        def exist(keyword):
            search_result = self.client.search(index=index, doc_type=doc_type, body={
                'query': {
                    'match': {
                        'keyword': keyword,
                    }
                }    
            })
            return search_result['hits']['total'] != 0

        if exist(info['keyword']):
            # TODO: update
            return

        self.client.index(index=index, doc_type=doc_type, id=info['keyword'], body=info)
