HTB - OpenAdmin
========================

![openadmininfo](https://github.com/jntxJ/Writeups/tree/master/HTB/OpenAdmin/images)

Esta maquina es 90% de enumeracion, veamos cuales son los pasos que seguiremos

- Enumeration
- Exploitation
- Privilege escalade

----------------

### Enumeration

Empecemos con el escaneo de red, usaremos `nmap`, el cual nos dara informacion sobre que puertos y servicios estan correindo sobre la maquina.

`nmap -sC -sV -p- --open -T4 -oN initialScan 10.10.10.171`

| Param  | Description   |
| -------|:------------- |
| -sC    | Muestra todos los scripts relacionados al servicio |
| -sV    | Nos permite ver las versiones de los servicios     |
| -p-    | Escaneo de todos los puertos                       |
| --open | Muestra solo los puertos abiertos                  |
| -T4    | Agresividad con la que hace el escaneo (-T{1-5})   |

![nmapInitial](/img/initialNmap)

Tenemos estos servicios corriendo:

- 22: SSH, proablemente nos sirva mas adelante
- 80: HTTP, empezaremos por aca a ver que tiene la pagina web

Veamos el servidor web

![defaultApache](/img/initialNmap)

Ok.. **. _.** nos muestra la pagina por default de apache, asi que usaremos herramientas que hacen fuerza bruta para ver si hay directorios o archivos activos.

En este caso usaremos `dirsearch` 

`dirsearch -u http://10.10.10.171/ -e html,php,js,json`
*Si le queremos indicar que busque cualquier extension, se usa `-E`*

![dsAll](/img/initialNmap)

Encontramos una carpeta y un archivo html. El html, nos redirecciona a la misma pagina por default.

Al ingresar a `/music`, nos mkustra:

![pageMusic](/img/initialNmap)

Despues de recorrer la pagina y encontrar solo hoyos de dudas, entre a el apartado `Login`.
 
Si nos fijamos, al tener el mouse sobre el, nos indica que nos movera a una nueva carpeta llamada`/ona`

**Ac'a hay algo importante y es que, siendo una sola web, no deberia estar `/ona` dentro de music? Osea `/music/ona`?**
esto toma fuerza mas adelante :P no nos volvamos locos.

![pageMusic](/img/initialNmap)

La pagina ya nos da informacion importante, estamos corriendo un servicio llamado **Open Net Admin** y su version **18.1.1**

**S:p** [OpenNetAdmin](http://opennetadmin.com/about.html) *es un sistema para el seguimiento de las propiedades de la red IP en una base de datos.* Basicamente permite rastrear toda la info gueardada en una db sobre una IP.

Despues de varios hoyos de dudas y sin saber que hacer con la interfaz, buscamos en linux a traves de una tool muy buena **searchsploit** que directamente es **exploidb** pero en la terminal. 

**S:_.** *[Exploit Database](https://www.exploit-db.com/) es una base de datos que aloja exploits y seguimientos de vulnerabilidades*

![ssploit](/img/initialNmap)

Para nuestra version solo nos sirven los dos ultimos, usaremos el que no dispone de *metasploit*

Con [searchsploit](https://www.exploit-db.com/searchsploit#using) podemos indicarle que nos deje ver el exploit y copiarlo a nuestro entorno (y muchas cosas mas)

| Param | Description   |
| ------|:------------- |
| -x, --examine | Ver el contenido del exploit          |
| -m, --mirror  | (aka copies) un exploit a nuestro entorno actual |

![exploitVi](/img/initialNmap)

Basicamente encontramos:

- Se debera ejecutar sobre bash
- Recibe como primer parametro la URL
- Esta enviando por medio de *curL* la data, envia el formato estandar que recibe *xajax*, pero tambien nos permite agregar comandos **${cmd}** para al final mandarla a la **${URL}**. 

Algo impirtante es que **no** estamos obteniendo una shell, simplemente estamos haciendo *command execution*, no podremos movernos a una carpeta en especifico, pero si podemos ver su contenido `cat` y listarlo `ls`

Al ejecutar el exploit, nos da varios errores... Despues de buscar cual era el error, encontramos que el archivo esta en formato **Dos (windows)**. Usamos la herramienta `dos2unix` que practicametne lo dice su nombre, convierte de `dos to unix`

![dos2unix](/img/initialNmap)

Listo!

Enumeracion y enumeracion, andando de carpeta en carpeta :) 

Hay 3 usuarios disponibles, 

- *www-data*: en el que estamos
- *jimmy*
- *joanna*

![db_settings_ex](/img/initialNmap)

Bien, conseguimos una pw. Veamos si es de alguno de los dos usuarios por medio de SSH

`ssh jimmy@10.10.10.171`

Sip!! Entramos al perfil de **jimmy**, sigamos enumerando.

No pondre todas las trampas en las que cai ;) pero encontramos algo despues de todo.

Si utilizamos el comando `id` notamos que estamos dentro del grupo `internal`

Veamos desde la raiz del sistema que archivos son de jimmy y estan asignados al grupo internal

`find / -user jimmy -group internal`

![jimmy_internal](/img/initialNmap)

Fijemonos en `main.php`

![main_php](/img/initialNmap)

Si conseguimos entrar a `/main.php` se ejecutara una consulta al *id_rsa (private key)* dentro del home de *joanna*, asi que veamos como hacer esa consulta

Arriba en el exploit se usaba *curL* para enviar la data a una URL especificada. Ac'a no es acaso lo mismo? solo que env vez de data queremos entrar en un archivo dentro de una carpeta?

`curl http://10.10.10.171/internal/main.php`

Pero esto simplemente nos muestra 

```sh
...
<title>404 Not Found</title>                                                                    
</head><body>                                                                                   
<h1>Not Found</h1>                                                                              
<p>The requested URL was not found on this server.</p>                                          
<hr>    
...
```

Asi que ac'a toma fuerza lo que habiamos olvidado arriba, sobre si estabamos trabajando sobre una sola web. Resulta que podemos configurar un sistema para que `internal`mente podamos alojar varios dominios sobre el mismo servidor, esto se llama **Virtual Host**, en este caso tenemos:

![internal_domains](1436242590.png)

- 10.10.10.171/music
- 10.10.10.171/ona
- 10.10.10.171/marga
- 10.10.10.171/artwork

Entonces el *curL* de arriba estar'ia mal, dado que no hay ning'un dominio llamado `internal`, pero probando sin el, tampoco obtenemos respuesta. Entonces la respuseta debe estar internamente en la configuracion del servidor.

Asi que vayamos a la configuracion de apache2 en `/etc/apache2`, revisando cada carpeta encontramos dentro de `/sites-enabled` dos archivos y en uno de ellos

![virtual_host_conf](1436242590.png)

Hay un **VirtualHost** corriendo sobre **localhost (127.0.0.1)** en el puerto **52846** en el que la informacion que esta alojando esta en **/var/www/internal** (que es la que vimos relacionada a `main.php`)

Asi que aca ya cambia la cosa, podemos hacer una petici'on con *curL* sobre esa info

![private_key_joanna](1436242590.png)

Perfecto, siempre tuvimos la pista en frente. **internal**

Guardamos esa llave en un archivo.

Intentamos conectarnos mediante la llave indicandole  `ssh -i file user@host` pero nos pide una password phrase para el **private key** que le estamos ingresando. 

Asi que debemos crackear mediante la llave la password del user :) 

Hay varias herramientas, usaremos [ssh2john.py](https://github.com/koboi137/john/blob/bionic/ssh2john.py) que efectivamente hace lo que necesitamos.

Al ejecutarlo obtenemos el hash que en este caso con `john` nos ayuda perfecto

![ssh2john_and_john](1436242590.png)

Obtenemos la password, intentando de nuevo la conexion, logramos entrar como **joanna**

![ssh2john_and_john](1436242590.png)

Listones, inicialmente tenemos la flag **user.txt**.
Tambien tenemos permisos como administrador a traves del binario **/bin/nano** (que es un editor de texto) sobre el archivo **/opt/priv**, lo que quiere decir que todo lo que hagamos con ese archivo lo estaremos haciendo como root.

![sudo_binNano](1436242590.png)

Buscando por internet nos encontramos con la herramienta [GTFOBins](https://gtfobins.github.io/gtfobins/nano/), que nos provee de una gran lista de como los binarios Unix pueden ser explotados, as'i que busquemos algo sobre *nano*

Nos dice que dentro de un archivo ejecutado por `nano` tenemos la opci'on de ejecutar comandos oprimiendo `Ctrl R + Ctrl X`, ac'a podemos hacerlo de varias formas, obtener una shell o simplemente eacribir los comandos y recibir la respuesta.

![nanocommandexecution](1436242590.png)

Para obtener una shell pondriamos, `reset; sh 1>&0 2>&0` y tendriamos una shell como root

![resetSH](1436242590.png)

O pasandole los comandos, nos imprimiria la respuesta en el mismo archivo **/opt/priv**

![commandwithnano](1436242590.png)

![headRoot_txt](1436242590.png)
