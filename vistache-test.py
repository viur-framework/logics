from logics.vistache import Template

x = Template("""Hello {{name}},

{{#persons}}{{name}} is {{age * 365}} days old{{#age > 33}}, and {{name * age}} is very old{{/}}
{{/}}
Sincerely,

{{author}}""")

print(x.render({"name": "Bernd", "author": "Jan", "persons": [{"name": "John", "age": 33}, {"name": "Doreen", "age": 25}, {"name": "Valdi", "age": 39}]}))
#print(x.render({"xxx": "Yolo", "persons": {"name": "John", "age": 33}}))
