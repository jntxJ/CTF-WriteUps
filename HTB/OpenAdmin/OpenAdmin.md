HTB - OpenAdmin
========================

![openadmininfo](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/infoopenadmin.PNG)

Esta maquina es 90% de enumeración, veamos cuáles son los pasos que seguiremos

- Enumeration
- Exploitation
- Privilege escalade

----------------

### Enumeration

Empecemos con el escaneo de red, usaremos `nmap`, el cual nos dará información sobre que puertos y servicios están corriendo sobre la maquina.

`nmap -sC -sV -p- --open -T4 -oN initialScan 10.10.10.171`

| Param  | Description   |
| -------|:------------- |
| -sC    | Muestra todos los scripts relacionados al servicio |
| -sV    | Nos permite ver las versiones de los servicios     |
| -p-    | Escaneo de todos los puertos                       |
| --open | Muestra solo los puertos abiertos                  |
| -T4    | Agresividad con la que hace el escaneo (-T{1-5})   |
| -oN    | Guardar el resultado en un archivo de texto        |

![nmapInitial](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/nmapInitial.png)

Tenemos estos servicios corriendo:

- 22: SSH, probablemente nos sirva mas adelante
- 80: HTTP, empezaremos por acá a ver que tiene la página web

Veamos el servidor web

![defaultApache](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/defaultApache.png)

Ok.. **. _.** nos muestra la página por default de apache, así que usaremos herramientas que hacen fuerza bruta para ver si hay directorios o archivos activos pero ocultos.

En este caso usaremos `dirsearch` 

`dirsearch -u http://10.10.10.171/ -e html,php,js,json`
*Si le queremos indicar que busque cualquier extension, se usa `-E`*

![dsAll](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/dsAll.png)

Encontramos una carpeta y un archivo html. El html, nos redirecciona a la misma pagina por default.

Al ingresar a `/music`:

![pageMusic](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/pageMusic.png)

Despues de recorrer la página y encontrar solo hoyos de dudas, entre a el apartado `Login`.
 
Si nos fijamos, al tener el mouse sobre él, nos indica que nos moverá a una nueva carpeta llamada `/ona`

![onaPage](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/onaPage.png)

**Acá hay algo importante y es que, siendo una sola web, no debería estar `/ona` dentro de music? Osea `/music/ona`?**
Esto toma fuerza más adelante :P no nos volvamos locos.

La página ya nos da información importante, estamos corriendo un servicio llamado **Open Net Admin** y su versión **18.1.1**

**nOTE:** [OpenNetAdmin](http://opennetadmin.com/about.html) *es un sistema para el seguimiento de las propiedades de la red IP en una base de datos.* Básicamente permite rastrear toda la info guardada en una db sobre una IP.

Después de varias dudas sin saber que hacer con la interfaz, recordamos una tool muy buena **searchsploit** que directamente es **exploidb** pero en la terminal. 

**nOTE:** [Exploit Database](https://www.exploit-db.com/) *es una base de datos que aloja exploits y seguimientos de vulnerabilidades*

![ssploit](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/ssploit.png)

Para nuestra versión solo nos sirven los dos últimos, usaremos el que no dispone de *metasploit*

Con [searchsploit](https://www.exploit-db.com/searchsploit#using) podemos indicarle que nos deje ver el exploit y copiarlo a nuestro entorno (y muchas cosas más).

| Param | Description   |
| ------|:------------- |
| -x, --examine | Ver el contenido del exploit          |
| -m, --mirror  | (aka copies) un exploit a nuestro entorno actual |

### Exploitation

![exploitVi](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/exploitVim.png)

Básicamente encontramos:

- Se deberá ejecutar sobre bash
- Recibe como primer parámetro la URL
- Está enviando por medio de *curL* la data, envía el formato estándar que recibe *xajax*, pero también nos permite agregar comandos **${cmd}** para al final hacer la petición a la **${URL}**.

Algo importante es que **no** estamos obteniendo una shell, simplemente estamos haciendo *command execution*, no podremos movernos a una carpeta en específico, pero si podemos ver su contenido `cat` y listarlo `ls`

Al ejecutar el exploit, nos da varios errores... Después de buscar cual era el error, encontramos que el archivo esta en el formato **DOS de (windows)**. Usamos la herramienta `dos2unix` que prácticamente lo dice su nombre, convierte de `dos to unix`

![dos2unix](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/dos2unix.png)

Listo!

Siguiendo con la enumeración y andando de carpeta en carpeta :):

Hay 3 usuarios disponibles, 

- *www-data*: en el que estamos
- *jimmy*
- *joanna*

...

![db_settings_ex](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/db_setting_ex.png)

Bien, conseguimos una pw. Veamos si es de alguno de los dos usuarios restantes por medio de SSH.

`ssh jimmy@10.10.10.171`

Sip!! Entramos al perfil de **jimmy**, sigamos enumerando. No pondre todas las trampas en las que cai ;) pero encontramos algo despues de todo. Si utilizamos el comando `id` notamos que estamos dentro del grupo `internal`

Veamos desde la raíz del sistema que archivos son de `jimmy` y estan asignados al grupo `internal`.

`find / -user jimmy -group internal`

![jimmy_internal](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/jimmy_internal.png)

Fijemonos en `main.php`

![main_php](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/main_php.png)

Si conseguimos entrar a `/main.php` se ejecutará una consulta al *id_rsa (private key)* dentro del home de *joanna*, asi que veamos como hacer esa consulta.

Arriba en el exploit se usaba *curL* para enviar la data a una URL especificada, ¿acá no es acaso lo mismo? solo que en vez de data queremos ver un archivo dentro de una carpeta.

`curl http://10.10.10.171/internal/main.php`

Pero esto simplemente nos muestra... 

```sh
...
<title>404 Not Found</title>                                                                    
</head><body>                                                                                   
<h1>Not Found</h1>                                                                              
<p>The requested URL was not found on this server.</p>                                          
<hr>    
...
```

Asi que acá toma fuerza lo que habiamos olvidado arriba, sobre si estabamos trabajando con una sola web. Resulta que podemos configurar un sistema para que **internal**mente podamos alojar varios dominios sobre el mismo servidor, esto se llama **Virtual Host**, en este caso tenemos:

![virtualhostdomains](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/virtual_host_domains.png)

- 10.10.10.171/music
- 10.10.10.171/ona
- 10.10.10.171/marga
- 10.10.10.171/artwork

Entonces el *curL* de arriba estaría mal, dado que no hay ningún dominio llamado `internal`, pero probando sin él, tampoco obtenemos respuesta. Entonces deberíamos **interna**mente buscar en la configuración del servidor.

Así que vayamos a la configuracion del servidor, en este caso apache2. Revisando `/etc/apache2`, verificando cada carpeta encontramos en `/sites-enabled` dos archivos y en uno de ellos:

![virtual_host_conf](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/virtual_host_conf.png)

Hay un **VirtualHost** corriendo sobre **localhost (127.0.0.1)** en el puerto **52846** en el que la información que esta alojando está en **/var/www/internal** (que es la que vimos relacionada a `main.php`)

Asi que acá ya cambia la cosa, podemos hacer una petición con *curL* sobre esa info

![private_key_joanna](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/private_key_joanna.png)

Perfecto, siempre tuvimos la pista en frente. (**internal**)

Guardamos esa llave en un archivo.

Intentamos conectarnos mediante la llave indicandole `ssh -i file user@host` pero nos pide una password phrase para el **private key** que le estamos ingresando. 

Así que debemos crackear mediante la llave la password de `joanna` :) 

Hay varias herramientas, usaremos [ssh2john.py](https://github.com/koboi137/john/blob/bionic/ssh2john.py) que efectivamente hace lo que necesitamos. Al ejecutarlo obtenemos el hash

![ssh2john_private](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/ssh2john_private.png)

Y usando John The Ripper, obtenemos la contraseña.

![ssh2john_and_john](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/ssh2john_and_john.png)

Intentando de nuevo la conexión, logramos entrar como **joanna**

![sshconnectjoanna](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/sshconecttojoanna.png)

Listones

![usertxtandsudo](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/usertxt_sudoL_id.png)

Inicialmente tenemos la flag **user.txt**.

### Privilege Escalation

También tenemos permisos como administrador a través del binario **/bin/nano** (que es un editor de texto) sobre el archivo **/opt/priv**, lo que quiere decir que todo lo que hagamos con ese archivo lo estaremos haciendo como root.

![sudobinnano](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/sudo_binNano_optPriv.png)

Buscando por internet nos encontramos con la herramienta [GTFOBins](https://gtfobins.github.io/gtfobins/nano/), que nos provee de una gran lista de como los binarios Unix pueden ser explotados, as'i que busquemos algo sobre *nano*

![gtfoNano](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/gtfoNano.PNG)

Nos dice que dentro de un archivo ejecutado por `nano` tenemos la opción de ejecutar comandos oprimiendo `Ctrl R + Ctrl X`, acá podemos hacerlo de dos formas, obtener una shell o simplemente escribir los comandos y recibir la respuesta.

![nanocommandexecution](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/nanocommandexecution.png)

Para obtener una shell pondríamos, `reset; sh 1>&0 2>&0` y tendríamos una shell como root

![resetSH](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/resetSH.png)

O pasandole los comandos, nos imprimiría la respuesta en el mismo archivo **/opt/priv**

![commandwithnano](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/commandwithnano.png)

Y listo, haciendo lo mismo podemos llegar a ver el contenido de **root.txt**

![headRoot_txt](https://github.com/jntxJ/Writeups/blob/master/HTB/OpenAdmin/images/headRoot_txt.png)
