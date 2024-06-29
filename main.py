import psycopg2 as pc
import sys

client = pc.connect("dbname=postgres user=postgres password=654321")
cursor = client.cursor()
#Default to accounts
db = "accounts"
if len(sys.argv) > 1:
    db = sys.argv[1]
if len(sys.argv) > 2:
    pkey = sys.argv[2]

cursor.execute("SELECT * from " + db)

list = cursor.fetchall()

cursor.execute("SELECT column_name, data_type, \
               character_maximum_length, is_nullable, column_default \
                FROM information_schema.columns \
                WHERE table_name = '" + db + "'")
prop = cursor.fetchall()
print(prop)
cursor.execute("SELECT column_name FROM information_schema.constraint_column_usage INNER JOIN information_schema.table_constraints \
               USING (constraint_name, table_name) WHERE constraint_type = 'PRIMARY KEY' AND table_name = '%s'" %(db))

pkey = cursor.fetchall()[0][0] or None

sc = {
    "character varying": "CHARVAR(%i)",
    "integer": "INT",
}
#Construct table
t = []
s = []
pIndex =-1
for i in range(0, len(prop)):
    v = prop[i]
    if pkey == v[0]:
        pIndex = i
    else:
        s.append((pkey != v[0] and v[0] or ""))
    t.append(v[0] + " " + (pkey == v[0] and "SERIAL" or sc[v[1].replace("[]", "")] % (v[2])) + ("[]" in v[1] and "[]" or "" ) + (pkey == v[0] and " PRIMARY KEY" or ""))
    

args = ",".join(t)
keys = ",".join(s)
ex1 = "CREATE TABLE %s (%s);" % (db, args)

k = []
for i in range(0, len(list)):
    if i != pIndex:
        v = list[i]
        l = []
        for j in range(0, len(v)):
            
            if "[]" not in t[i]:
                l.append( "'%s'"%(str(v[j])) )
            else:
                for w in len(0, v[j]):
                    v[j][w] = str(v[j][w])
                l.append("ARRAY [%s]:: %s"%( ",".join(v[j]) ), prop[j][1] )
        l = ",".join(l)
        k.append("(%s)"%( l ))


ex2 = "INSERT INTO %s (%s) VALUES %s;" % (db, keys, ",".join(k)) 
print(ex1 , "\n", ex2)
#Fill table
