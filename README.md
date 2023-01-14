Business logic
---

- Scrape data from website
- Retrieve data from database
- Create excel document



Scrape data from website
---

**update endpoint:**
`{{host}}/update`
```json
{
  "message": "updated"
}
```
**retrieve data:**
`{{host}}/sales/?from=<from_date>&to=<to_date>`

**create excel document:**
`{{host}}/to_excel`


