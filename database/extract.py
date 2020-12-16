import json

with open('data/saef.json') as json_file:
    data = json.load(json_file)
    
    data_dict = {}
    
    for x in data:
        name = x['model']
        
        if name not in data_dict:
            data_dict[name] = []
            
        data_dict[name].append(x)
    
    
    for key, model in data_dict.items():
        with open(f'data/{key}.json', 'w', encoding='utf-8') as f:
            json.dump(model, f, ensure_ascii=False, indent=2)
    