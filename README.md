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

'''python
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
'''
