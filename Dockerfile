FROM ubuntu:latest as builder

RUN apt-get -yq update && apt-get -yq install subversion make wget unzip file make autoconf gcc g++ flex bison dos2unix xa65 libcurl4-openssl-dev pkg-config zlib1g-dev python3-pytest python3-zstandard python3-psutil git
RUN svn co --non-interactive --trust-server-cert https://svn.sngs.de/metalvotze/svn/repo/mufflon/
RUN wget http://csdb.dk/getinternalfile.php/97492/NUVIEmaker-0.1e.zip
WORKDIR /nuvie
RUN unzip -j ../NUVIE*.zip
WORKDIR /mufflon
RUN make && cp mufflon /usr/local/bin

WORKDIR /vice
RUN git clone https://github.com/anarkiwi/asid-vice
WORKDIR /vice/asid-vice
RUN aclocal && autoheader && autoconf && automake --force-missing --add-missing && ./autogen.sh && \
    ./configure --enable-headlessui --disable-pdf-docs --without-pulse --without-alsa --without-png --disable-dependency-tracking --disable-realdevice --disable-rs232 --disable-ipv6 --disable-native-gtk3ui --disable-sdlui --disable-sdlui2 --disable-ffmpeg
RUN make -j all && make install

FROM ubuntu:latest
RUN apt-get -yq update && apt-get -yq install ffmpeg inetutils-telnet python3-pexpect parallel libcurl4 libgomp1 zlib1g python3 python3-psutil python3-zstandard
COPY makenuvie.py /usr/local/bin
COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /nuvie /nuvie
WORKDIR /work
ENTRYPOINT ["python3", "/usr/local/bin/makenuvie.py"]
