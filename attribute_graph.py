#!/usr/bin/env python
import os
import subprocess
from json import dumps
from flask import Flask, g, Response, request, render_template, jsonify

from neo4j import GraphDatabase, basic_auth

app = Flask(__name__)

url = os.getenv("NEO4J_URL","bolt://127.0.0.1:******")
password = os.getenv("NEO4J_PASSWORD","********")

uri = "neo4j://localhost:*******"

driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", password), encrypted=False)

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/graph', methods=['GET','POST'])
def my_form_post():
      source = request.form['source']
      target = request.form['target']
      db = get_db()
      results = db.run("MATCH t=(n)-[q*]->(p) WHERE n.name= '"+source+"' and p.name='"+target+"' RETURN reduce(s='', node in nodes(t) | s+node.name+',') as `node names`")
      results1= db.run("MATCH t=(n)-[q*]->(p) WHERE n.name= '"+source+"' and p.name='"+target+"' RETURN reduce(s='', rel in relationships(t) | s+rel.label+',') as `rel types`")
      results2= db.run("MATCH t=(n)-[q*]->(p) WHERE n.name= '"+source+"' and p.name='"+target+"' RETURN reduce(x = 1.0, rel in relationships(t) | x * toFloat(rel.`degree of similarity`)) as `degree of similarity`")
      nodes=[];
      rels=[];
      dos=[];
      for record in results:
          nodelist=record['node names'].split(',');              ##    Extracting Nodes
          nodelist = list(filter(None, nodelist)); 
          nodes.append(nodelist);
      #print(len(nodes));
      for record in results1:
          rellist=record['rel types'].split(',');
          rellist= list(filter(None, rellist));                  ## Extracting Relations             
          rels.append(rellist);
      #print(len(rels));
      for record in results2:                                      
          dos.append(record['degree of similarity']);            ## Extracting Degree of Similarity
      #print(len(dos));                                           
      value = max(dos);
      #print (value);      
      map={}; 
      index = dos.index(value);
      for i in nodes[index]:
         if (i != source and i != target):                      ## Finding the index of the path with maximum degree of similarity
            map[i] = 'True';
      print(map);
      valid_index=[];
      for i in range(0, len(nodes)):
         if (i != index):                                       ## Checking the path if the node was already traversed by the path with highest dos.
           for j in nodes[i]:
               if j in map:
                 valid_index.append(i);                       
      unique_index = list(set(valid_index));
      for offset, index in enumerate(unique_index):
         index -= offset;
         del nodes[index];                                       ## Deleting the paths without valid path
         del rels[index];
         del dos[index];
      print (len(nodes), len(rels), len(dos))
      rel_index=[];
      for i in range(len(rels)):
         for x in range(0, len(rels[i])):
            heirarchy,type=rels[i][x].split('-')  
            for j in range(x+1, len(rels[i])):
               heirarchy1,type1=rels[i][j].split('-')          ## Checking if the relations of same heirarchy have different type of relations
               if heirarchy == heirarchy1:
                  if type != type1:
                    rel_index.append(i);
      unique_index = list(set(rel_index));
      #print(unique_index);
      for offset, index in enumerate(unique_index):
         index -= offset;
         del nodes[index];
         del rels[index];
         del dos[index];
      print (nodes, rels, dos)
      if not nodes:
         result = {
             "output": "NO Valid Path"
         }
      else:
         result = {
             "output": str(len(nodes))+ "Valid Path Exists!!!!!!!",
             "Nodes_in the path": ["{"+str(nodes[i])+"}" for i in range(len(nodes))],
             "Relations in the path": ["{"+str(rels[i])+"}" for i in range(len(rels))],
             "degree of similarity": dos
         }
      result = {str(key): value for key, value in result.items()}
      return jsonify(result=result)

if __name__ == '__main__':
    app.run(port=********)
