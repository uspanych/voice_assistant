
def get_body_search_with_films(
        value: str,
        field: str,
        size: int = None,
        offset: int = None,
):

    query = {
        'query': {
            'bool': {
                'should': [
                    {
                        'nested': {
                            'path': 'directors',
                            'query': {
                                'bool': {
                                    'must': [
                                        {
                                            'match': {
                                                f'directors.{field}': value
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    {
                        'nested': {
                            'path': 'actors',
                            'query': {
                                'bool': {
                                    'must': [
                                        {
                                            'match': {
                                                f'actors.{field}': value
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    {
                        'nested': {
                            'path': 'writers',
                            'query': {
                                'bool': {
                                    'must': [
                                        {
                                            'match': {
                                                f'writers.{field}': value
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

    if (size and offset) is not None:
        return {
            'query': query,
            "from": offset,
            "size": size,
        }
    else:
        return query


def get_body_search(
        size: int,
        sort_by: str,
        offset: int,
        sort_order: str,
        genre: str | None = None,
        actor: str | None = None,
        director: str | None = None,
        writer: str | None = None,
):
    """Функция формирует тело запроса к ElasticSearch."""

    if not any([genre, actor, director, writer]):
        return {
            "sort": [
                {
                    sort_by: {
                        "order": sort_order,
                    }
                }
            ],
            "from": offset,
            "size": size,
        }
    fields = []

    if genre is not None:
        fields.append(
            {
                'field': 'genres',
                'id': genre,
            }
        )

    if actor is not None:
        fields.append(
            {
                'field': 'actors',
                'id': actor,
            }
        )

    if writer is not None:
        fields.append(
            {
                'field': 'writers',
                'id': writer,
            }
        )

    if director is not None:
        fields.append(
            {
                'field': 'directors',
                'id': director,
            }
        )

    query = _get_query(fields)

    return {
        "query": query,
        "sort": [
            {
                sort_by: {
                    "order": sort_order,
                }
            }
        ],
        "from": offset,
        "size": size,
    }


def get_body_query(
        field: str,
        value: str,
        offset: int,
        size: int,
) -> dict:
    query = {
        "query": {
            "match": {
                f"{field}": {
                    "query": f"{value}",
                    "fuzziness": "auto"
                }
            }
        },
        "from": offset,
        "size": size,
    }

    return query


def _get_query(
        fields: list
) -> dict:
    query = {
        "bool": {
            "should": [
            ]
        }
    }
    for item in fields:
        query['bool']['should'].append(
            _get_nested(
                item.get('field'),
                item.get('id'),
            )
        )

    return query


def _get_nested(
        path: str,
        field: str
) -> dict:
    return {
        "nested": {
            "path": path,
            "query": {
                "bool": {
                    "must": [
                        {"match": {f"{path}.id": field}}
                    ]
                }
            }
        }
    }
