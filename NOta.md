# NOta

Mon, Jul 3, 2023 8:51 PM

<br>
docker network create my-network 

docker run --name my-neo4j-container --network=my-network -p 7474:7474 -p 7687:7687 -v C:\\Users\\Diego\\.Neo4jDesktop\\relate-data\\dbmss\\dbms-bb518441-44e0-4620-86cc-5e15e251526f\\data\\databases\\data -v /path/to/save/data:/data neo4j 

docker run -p 8000:8000 --network=my-network --name conection\_container -v C:/Users/Diego/app\_conection:/app app\_conection