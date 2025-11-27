from datetime import date, timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

fecha_reserva = date(2025, 12, 15)
fecha_checkin = fecha_reserva.strftime("%Y-%m-%d")
fecha_checkout = (fecha_reserva + timedelta(days=1)).strftime("%Y-%m-%d")

destinos = {
    # "Mendoza": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Mendoza&ssne=Provincia+de+Mendoza&ssne_untouched=Provincia+de+Mendoza&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQGIAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIF4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=597&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Buenos Aires": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Buenos+Aires&ssne=Provincia+de+Buenos+Aires&ssne_untouched=Provincia+de+Buenos+Aires&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQzYAQHoAQGIAgGoAgO4As24scEGwAIB0gIkMjI2YjA4N2MtM2MyOS00YmM5LTlkYjItOWYzN2Y0OWJkZjY32AIF4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3619&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "CABA": f"https://www.booking.com/searchresults.es.html?ss=Buenos+Aires%2C+Argentina&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQGIAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIF4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=-979186&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6d714bad82ea0156&ac_meta=GhA2ZDcxNGJhZDgyZWEwMTU2IAAoATICZXM6CUNpdWRhZCBhdUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Córdoba": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+C%C3%B3rdoba%2C+Argentina&ssne=C%C3%B3rdoba&ssne_untouched=C%C3%B3rdoba&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=1342&dest_type=region&ac_position=2&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=33464bddd7f40901&ac_meta=GhAzMzQ2NGJkZGQ3ZjQwOTAxIAIoATICZXM6FVByb3ZpbmNpYSBkZSBDw7NyZG9iYUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Santa Fe": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Santa+Fe&ssne=Provincia+de+Santa+Fe&ssne_untouched=Provincia+de+Santa+Fe&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3628&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Neuquén": f"https://www.booking.com/searchresults.es.html?ss=Neuqu%C3%A9n+Province%2C+Argentina&ssne=Provincia+de+Santa+Fe&ssne_untouched=Provincia+de+Santa+Fe&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=3627&dest_type=region&ac_position=2&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6f6c4c269cd101aa&ac_meta=GhA2ZjZjNGMyNjljZDEwMWFhIAIoATICZXM6CE5ldXF1w6luQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Salta": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Salta%2C+Argentina&ssne=Salta&ssne_untouched=Salta&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=599&dest_type=region&ac_position=1&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=9a3a4c9baf610170&ac_meta=GhA5YTNhNGM5YmFmNjEwMTcwIAEoATICZXM6ElByb3ZpbmNpYSBkZSBTYWx0YUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Jujuy": f"https://www.booking.com/searchresults.es.html?ss=Jujuy&ssne=Jujuy&ssne_untouched=Jujuy&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=596&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Tucumán": f"https://www.booking.com/searchresults.es.html?ss=Tucum%C3%A1n&ssne=Tucum%C3%A1n&ssne_untouched=Tucum%C3%A1n&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3629&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Formosa": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Formosa&ssne=Provincia+de+Formosa&ssne_untouched=Provincia+de+Formosa&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3624&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Santiago del Estero": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Santiago+del+Estero&ssne=Provincia+de+Santiago+del+Estero&ssne_untouched=Provincia+de+Santiago+del+Estero&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=602&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "La Rioja": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+La+Rioja%2C+Argentina&ssne=Provincia+de+Santiago+del+Estero&ssne_untouched=Provincia+de+Santiago+del+Estero&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3626&dest_type=region&ac_position=1&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=290b4ddeba5d0463&ac_meta=GhAyOTBiNGRkZWJhNWQwNDYzIAEoATICZXM6FVByb3ZpbmNpYSBkZSBMYSBSaW9qYUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "San Juan": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+San+Juan&ssne=Provincia+de+San+Juan&ssne_untouched=Provincia+de+San+Juan&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=600&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "San Luis": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+San+Luis&ssne=Provincia+de+San+Luis&ssne_untouched=Provincia+de+San+Luis&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=601&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "La Pampa": f"https://www.booking.com/searchresults.es.html?ss=La+Pampa&ssne=La+Pampa&ssne_untouched=La+Pampa&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3625&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Río Negro": f"https://www.booking.com/searchresults.es.html?ss=R%C3%ADo+Negro&ssne=R%C3%ADo+Negro&ssne_untouched=R%C3%ADo+Negro&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=598&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Santa Cruz": f"https://www.booking.com/searchresults.es.html?ss=Santa+Cruz&ssne=Santa+Cruz&ssne_untouched=Santa+Cruz&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=3618&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Catamarca": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Catamarca&ssne=Provincia+de+Catamarca&ssne_untouched=Provincia+de+Catamarca&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3620&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Misiones": f"https://www.booking.com/searchresults.es.html?ss=Misiones&ssne=Misiones&ssne_untouched=Misiones&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=1343&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Tierra del Fuego": f"https://www.booking.com/searchresults.es.html?ss=Tierra+del+Fuego&ssne=Tierra+del+Fuego&ssne_untouched=Tierra+del+Fuego&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=603&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Corrientes": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Corrientes&ssne=Provincia+de+Corrientes&ssne_untouched=Provincia+de+Corrientes&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3623&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Entre Ríos": f"https://www.booking.com/searchresults.es.html?ss=Entre+R%C3%ADos&ssne=Entre+R%C3%ADos&ssne_untouched=Entre+R%C3%ADos&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=595&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Chaco": f"https://www.booking.com/searchresults.es.html?ss=Chaco&ssne=Chaco&ssne_untouched=Chaco&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3621&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Chubut": f"https://www.booking.com/searchresults.es.html?ss=Chubut&ssne=Chubut&ssne_untouched=Chubut&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3622&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Río de Janeiro": f"https://www.booking.com/searchresults.es.html?ss=R%C3%ADo+de+Janeiro%2C+R%C3%ADo+de+Janeiro%2C+Brasil&ssne=R%C3%ADo+de+Janeiro&ssne_untouched=R%C3%ADo+de+Janeiro&efdco=1&label=gen173nr-10CAEoggI46AdIM1gEaAyIAQGYATO4ARfIAQzYAQPoAQH4AQGIAgGoAgG4AuzZwsQGwAIB0gIkNTg3Yzk4NDktNTE1MS00ZTZiLWE0YzEtOWFhMzQ5ZWRlM2I52AIB4AIB&sid=07e0f29184142cdd408cfbc94b0bd0ae&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=-666610&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=2bf15a907e0f088c&ac_meta=GhAyYmYxNWE5MDdlMGYwODhjIAAoATICZXM6CFLDrW8gZGUgQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Viña del Mar": f"https://www.booking.com/searchresults.es.html?ss=Vi%C3%B1a+del+Mar%2C+Valpara%C3%ADso+Region%2C+Chile&ssne=R%C3%ADo+de+Janeiro&ssne_untouched=R%C3%ADo+de+Janeiro&label=gen173nr-10CAEoggI46AdIM1gEaAyIAQGYATO4ARfIAQzYAQPoAQH4AQGIAgGoAgG4AuzZwsQGwAIB0gIkNTg3Yzk4NDktNTE1MS00ZTZiLWE0YzEtOWFhMzQ5ZWRlM2I52AIB4AIB&sid=dc1029d913a82d38c79bdb261886d12c&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=-904540&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6e7b5af4a3cc0d61&ac_meta=GhA2ZTdiNWFmNGEzY2MwZDYxIAAoATICZXM6BXZpw7FhQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD"
}


def inicializar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1366,768")
    # options.add_argument("--renderer-process-limit=3")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-background-timer-throttling")
    # options.add_argument("--disable-backgrounding-occluded-windows")
    # options.add_argument("--disable-renderer-backgrounding")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-infobars")
    # options.add_argument("--no-first-run")
    # options.add_argument("--no-default-browser-check")
    # options.add_argument("--disable-background-networking")
    # options.add_argument("--disable-default-apps")
    # options.add_argument("--disable-sync")
    # options.add_argument("--metrics-recording-only")
    # options.add_argument("--mute-audio")
    # options.add_argument("--no-zygote")
    # options.add_argument("--disable-software-rasterizer")

    # prefs = {
    #     "profile.managed_default_content_settings.images": 2,
    #     "profile.default_content_setting_values.notifications": 2,
    #     "profile.default_content_setting_values.geolocation": 2,
    #     "profile.default_content_setting_values.sound": 2,
    # }

    # options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(15)

    # driver.execute_cdp_cmd("Network.enable", {})
    # driver.execute_cdp_cmd("Network.setBlockedURLs", {
    #     "urls": [
    #         "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp",
    #         "*.svg", "*.mp4", "*.webm", "*.avi", "*.mov",
    #         "*.woff", "*.woff2", "*.ttf", "*.otf"
    #     ]
    # })

    return driver


def parsear_a_float(num_string: str):
    if ("US$" in num_string):
        num_sin_signo = num_string.replace("US$", "").strip()
        num_corregido = num_sin_signo.replace(".", "").replace(",", ".")
    elif (num_string == ''):
        num_corregido = "0"
    else:
        num_corregido = num_string.replace(".", "").replace(",", ".")
    return float(num_corregido)
