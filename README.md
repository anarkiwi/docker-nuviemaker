# docker-nuviemaker

Automates most of the process to generate a https://www.c64-wiki.de/wiki/Nuvie. Source video must be sized to 320x200.

```
$ docker run -v /scratch/tmp:/iod -ti nuviemaker zardoz.mp4
$ ls -l /scratch/tmp/zardoz.*
-rw-r--r-- 1 josh josh  1057575 Jun  1 09:05 /scratch/tmp/zardoz.mp4
-rw-r--r-- 1 root root 16777216 Jun 16 18:59 /scratch/tmp/zardoz.reu
```
