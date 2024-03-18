def get_display_items(style_element):
    display_items = []

    for item in style_element.find('display'):
        display_items.append({
            'metric': item.find('metric').text,
            'posx': item.find('posx').text,
            'posy': item.find('posy').text,
            'width': item.find('width').text,
            'height': item.find('height').text,
            'theme': item.find('theme').text,
            'color': item.find('color').text
        })
    
    return display_items