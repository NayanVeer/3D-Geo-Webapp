# routes/utils/keyword_mapping.py

def get_layer_filters(type_keyword: str):
    keyword = type_keyword.lower()
    
    mappings = {
        # Generic categories
        "hospital": [{"table": "place_points", "field": "fclass"}],
        "school": [{"table": "place_points", "field": "fclass"}],
        "college": [{"table": "place_points", "field": "fclass"}],
        "bus": [{"table": "transport_stops", "field": "fclass"}],
        "rail": [{"table": "railway", "field": "fclass"}],
        "traffic": [{"table": "traffic_point", "field": "fclass"}],
        "hotel": [{"table": "place_points", "field": "fclass"}],
        "bank": [{"table": "place_points", "field": "fclass"}],
        "atm": [{"table": "place_points", "field": "fclass"}],

        # Station may exist in multiple tables
        "station": [
            {"table": "transport_stops", "field": "fclass"},
            {"table": "railway", "field": "fclass"},
        ],

        # Religious categories with specific fclass values
        "temple": [{"table": "worship_places", "field": "fclass", "value": "hindu"}],
        "mandir": [{"table": "worship_places", "field": "fclass", "value": "hindu"}],
        "mosque": [{"table": "worship_places", "field": "fclass", "value": "muslim"}],
        "church": [{"table": "worship_places", "field": "fclass", "value": "christian"}],
        "gurudwara": [{"table": "worship_places", "field": "fclass", "value": "sikh"}],
    }

    # Fallback: scan all major layers if no specific mapping found
    fallback_tables = [
        {"table": "places", "field": "fclass"},
        {"table": "place_points", "field": "fclass"},
        {"table": "traffic_point", "field": "fclass"},
        {"table": "worship_places", "field": "fclass"},
        {"table": "transport_stops", "field": "fclass"},
        {"table": "railway", "field": "fclass"},
    ]

    return mappings.get(keyword, fallback_tables)
