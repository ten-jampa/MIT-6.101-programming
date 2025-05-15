# Recitation code (May 12, 2024)
# Understanding code other people have written

import requests
base_url = 'https://hz.mit.edu/drawings'

ID = '46oyrqalv1'

for x in range(50, 150):
        y = 100
        print(requests.post(f'{base_url}/set_pixel',
                           data = {
                               'image': ID,
                               'x': x,
                               'y': y,
                               'color': "[240, 100, 30]"
						   } 
                        ))
