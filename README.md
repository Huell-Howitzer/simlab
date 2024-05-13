# simlab


| Date   | LS | RG |
|--------|----|----|
| 02/26  | 9  | 0  |
| 02/27  | 0  | 9  |
| 02/28  | 9  | 0  |
| 02/29  | 0  | 9  |
| 03/05  | 0  | 9  |
| 03/06  | 4  | 5  |
| 03/06  | 9  | 0  |
| 03/07  | 9  | 0  |
| 03/08  | 2  | 6  |

```python
from SPARQLWrapper import SPARQLWrapper, JSON

# Initialize the SPARQL wrapper for Wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
query = """
SELECT ?mass
WHERE {
  wd:Q293743 wdt:P2067 ?mass         # Q293743 is the AMRAAM missile
}
"""
sparql.setQuery(query)
sparql.setReturnFormat(JSON)

# Execute the query and fetch the results
results = sparql.query().convert()
if results["results"]["bindings"]:
    for result in results["results"]["bindings"]:
        mass = result["mass"]["value"]
        print(f"The mass of the AMRAAM missile is {mass} kg (assuming kilograms as the unit).")
else:
    print("No mass data available for the AMRAAM missile.")
```



https://www.coursera.org/account/accomplishments/verify/AW6E4W4WX5BG?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course



https://www.coursera.org/account/accomplishments/verify/A8KGW5C74DDV?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course

https://www.coursera.org/account/accomplishments/verify/9KXX6QHGXA6X?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course

https://www.coursera.org/account/accomplishments/verify/GMGTR3V7D5ZX?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course

https://www.coursera.org/account/accomplishments/verify/46CFLTTZAH23?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course

https://wwww.coursera.org/account/accomplishments/specialization/GYQB8ELADGD5

https://www.coursera.org/account/accomplishments/verify/PRFEMXVKRFKJ?utm_source=ios&utm_medium=certificate&utm_content=cert_image&utm_campaign=sharing_cta&utm_product=course
