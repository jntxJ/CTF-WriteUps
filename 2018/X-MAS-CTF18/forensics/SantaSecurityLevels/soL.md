# Santa's Security Levels
#### Pts : 50  
#### Santa has a flag hidden for you! Find out where. All letters, except for the X-MAS header, are lowercase.
#### (Flag is Non-Standard, please add X-MAS{ } to the found string)
#### Author: Googal

---

Nos dan un .MP3, lo ejecutamos, hay un tipo de interferencia, presuntamente es [morse](https://en.wikipedia.org/wiki/Morse_code)

Abro el archivo en [Audacity](https://www.audacityteam.org/), vemos que podemos asociar (a morse) los cambios de tono con `.` y `-` ya que hay intervalos mas largos, eso nos da la diferencia.

![alt text](https://github.com/jntxJ/CTF-WriteUps/blob/master/2018/X-MAS-CTF18/forensics/SantaSecurityLevels/Audacity.png)

Obtengo esto:

    --. .. - .... ..- -... -.-. --- -- --. --- --- --- --. .- .-.. -..- -- .- ...

Al usar un traductor morse online, obtengo esta frase

    githubcomgooogalxmas

Aca he estado en un punto de interrupcion (y locura), claramente se ve que dice xmas(nombre del ctf), tambien dice github, 
pero, no me toma como valido para la bandera, intente ponerle `_` a la frase pero tampoco. Intente ir a un tipo de dominio... 

    github.com/gooogalxmas

Tampoco sirvio :(    
incluso googlearlo, pero no sale nada relacionado.

### Bingo! 

Intente otra que me parecio buena

    github.com/gooogal
    
[github.com/gooogal](https://github.com/gooogal)

Busque su ultima actualizacion y tenia 2 commits y un repositorio llamado xmas :O
(correct road)

Seguimos el camino.

https://github.com/Gooogal/xmas/blob/master/special%20message.txt

Al entrar nos encontramos un txt > special message.txt

> Santa doesn't like people searching for his flags, but you look like a nice person. 
> Anyway here's your flag:

> vF ur uNq nAlguvat pbasvqraGvNy gb fnl, ur jebgr Vg ia pvcure, gung vF, ol FB punaTvat gur beqre bs gur Yrggref bs gur nycuNorg, gung abg n j    beQ pbhyq or ZnQR bHg.

Lo primero que recorde fue [Caesar](https://en.wikipedia.org/wiki/Caesar_cipher), asi que lo converti.

    ISHEHADANYTHINGCONFIDENTIALTOSAYHEWROTEITVNCIPHERTHATISBYSOCHANGINGTHEORDEROFTHELETTERSOFTHEALPHABETTHATNOTAWORDCOULDBEMADEOUT

Curiosamente el texto claro lo descifra 13 posiciones adelante. 
Decido hacer otra cosa. 

Por la posicion de las letras del [special message.txt](https://github.com/jntxJ/CTF-WriteUps/blob/master/2018/X-MAS-CTF18/forensics/SantaSecurityLevels/special_message.md) 
y por que me dejo pensativo, recuerdo a [Rot13](https://en.wikipedia.org/wiki/ROT13). La converti y el resultado fue este.

    iS he hAd aNything confidenTiAl to say, he wrote It vn cipher, that iS, by SO chanGing the order of the Letters of the alphAbet, that not a w    orD could be MaDE oUt

Es muy comun encontrar esto en retos, letras en mayusculas donde no deberian ir, eso nos da una pista. Tomemos todas las letras mayusculas y formemos una cadena

    SANTAISSOGLADMDEU

Efectivamente!!
Tenemos la FLAG
Recordemos que el reto nos dice que la flag debe ir en minuscula y le debemos agregar el xmas al inicio.

La bandera por lo tanto queda asi:

    X-MAS{santaissogladmdeu}

This challenge was fun and pretty

### I'm new in computer security and i'm loving this. 

