# $RCSfile: Makefile.SH,v 99596Revision: 4.1 99596Date: 92/08/07 18:29:07 $
#
# $Log:	Makefile.SH,v $

CC = cc
BYACC = byacc
LDFLAGS = -Wl,-E  -L/usr/local/lib
# XXX Perl malloc temporarily unusable (declaration collisions with stdlib.h)
#mallocsrc = 
#mallocobj = 
shellflags = 

libs = -lm -lcrypt -lutil -lc

#
# grrr
SHELL = /bin/sh

# These variables may need to be manually set for non-Unix systems.
AR = ar
EXE_EXT = 
LIB_EXT = .a
OBJ_EXT = .o
PATH_SEP = :

FIRSTMAKEFILE = makefile

# how to tr(anslate) newlines

TRNL = '\n'

OPTIMIZE = -O

.SUFFIXES: .c $(OBJ_EXT)


REALPERL = ../perl
CCCMD = `sh $(shellflags) cflags "optimize='$(OPTIMIZE)'" $@`

public = a2p$(EXE_EXT) s2p find2perl

private = 

manpages = a2p.man s2p.man

util =

sh = Makefile.SH cflags.SH
shextract = Makefile cflags

pl = find2perl.PL s2p.PL
plextract = find2perl s2p
plexe = find2perl.exe s2p.exe
plc   = find2perl.c s2p.c
plm   = a2p.loadmap

addedbyconf = $(shextract) $(plextract)

h = EXTERN.h INTERN.h ../config.h ../handy.h hash.h a2p.h str.h util.h

c = hash.c $(mallocsrc) str.c util.c walk.c

obj = hash$(OBJ_EXT) $(mallocobj) str$(OBJ_EXT) util$(OBJ_EXT) walk$(OBJ_EXT)

lintflags = -phbvxac


.c$(OBJ_EXT):
	$(CCCMD) -DPERL_FOR_X2P $*.c

all: $(public) $(private) $(util)
	@echo " "

compile: all
	$(REALPERL) -I../lib ../utils/perlcc -I .. -L .. $(plextract) -v -log ../compilelog;  

a2p$(EXE_EXT): $(obj) a2p$(OBJ_EXT)
	$(CC) -o a2p $(LDFLAGS) $(obj) a2p$(OBJ_EXT) $(libs)

# I now supply a2p.c with the kits, so the following section is
# used only if you force byacc to run by saying
#    make run_byacc
# byacc 1.8.2 or 1.9 are recommended.

run_byacc:	FORCE
	@ echo Expect many shift/reduce and reduce/reduce conflicts
	$(BYACC) a2p.y
	rm -f a2p.c
	sed -e 's/(yyn = yydefred\[yystate\])/((yyn = yydefred[yystate]))/' \
	    -e 's/(yys = getenv("YYDEBUG"))/((yys = getenv("YYDEBUG")))/' \
	    -e 's/^yyerrlab://' \
	    -e 's/^    goto yyerrlab;//' \
	    -e 's/^yynewerror://' \
	    -e 's/^    goto yynewerror;//' \
	    -e 's|^static char yysccsid\(.*\)|/* static char yysccsid\1 */|' \
	    < y.tab.c > a2p.c

FORCE:

# We don't want to regenerate a2p.c, but it might appear out-of-date
# after a patch is applied or a new distribution is made.
a2p.c: a2p.y
	-@sh -c true

a2p$(OBJ_EXT): a2p.c a2py.c a2p.h EXTERN.h util.h INTERN.h \
		../handy.h ../config.h str.h hash.h
	$(CCCMD) a2p.c

clean:
	rm -f a2p$(EXE_EXT) psed *$(OBJ_EXT) $(plexe) $(plc) $(plm)

realclean: clean
	-rmdir .depending
	rm -f core $(addedbyconf) all malloc.c
	rm -f $(FIRSTMAKEFILE) $(FIRSTMAKEFILE).old makefile.old

veryclean: realclean
	rm -f *~ *.orig

# The following lint has practically everything turned on.  Unfortunately,
# you have to wade through a lot of mumbo jumbo that can't be suppressed.
# If the source file has a /*NOSTRICT*/ somewhere, ignore the lint message
# for that spot.

lint:
	lint $(lintflags) $(defs) $(c) > a2p.fuzz

depend: $(mallocsrc) ../makedepend
	sh ../makedepend MAKE=$(MAKE)

clist:
	echo $(c) | tr ' ' $(TRNL) >.clist

hlist:
	echo $(h) | tr ' ' $(TRNL) >.hlist

shlist:
	echo $(sh) | tr ' ' $(TRNL) >.shlist

# These should be automatically generated

$(plextract):
	../miniperl -I../lib $@.PL

find2perl: find2perl.PL

s2p: s2p.PL

malloc.c: ../malloc.c
	rm -f malloc.c
	sed <../malloc.c >malloc.c \
	    -e 's/"EXTERN.h"/"..\/EXTERN.h"/' \
	    -e 's/"perl.h"/"..\/perl.h"/' \
	    -e 's/my_exit/exit/' \
	    -e 's/MUTEX_[A-Z_]*(&PL_malloc_mutex);//'

# AUTOMATICALLY GENERATED MAKE DEPENDENCIES--PUT NOTHING BELOW THIS LINE
# If this runs make out of memory, delete /usr/include lines.
hash$(OBJ_EXT): ../config.h
hash$(OBJ_EXT): ../handy.h
hash$(OBJ_EXT): /usr/include/_ctype.h
hash$(OBJ_EXT): /usr/include/ctype.h
hash$(OBJ_EXT): /usr/include/inttypes.h
hash$(OBJ_EXT): /usr/include/machine/_inttypes.h
hash$(OBJ_EXT): /usr/include/machine/_limits.h
hash$(OBJ_EXT): /usr/include/machine/_stdint.h
hash$(OBJ_EXT): /usr/include/machine/_types.h
hash$(OBJ_EXT): /usr/include/machine/endian.h
hash$(OBJ_EXT): /usr/include/math.h
hash$(OBJ_EXT): /usr/include/runetype.h
hash$(OBJ_EXT): /usr/include/stdio.h
hash$(OBJ_EXT): /usr/include/stdlib.h
hash$(OBJ_EXT): /usr/include/string.h
hash$(OBJ_EXT): /usr/include/strings.h
hash$(OBJ_EXT): /usr/include/sys/_null.h
hash$(OBJ_EXT): /usr/include/sys/_pthreadtypes.h
hash$(OBJ_EXT): /usr/include/sys/_sigset.h
hash$(OBJ_EXT): /usr/include/sys/_timeval.h
hash$(OBJ_EXT): /usr/include/sys/_types.h
hash$(OBJ_EXT): /usr/include/sys/cdefs.h
hash$(OBJ_EXT): /usr/include/sys/select.h
hash$(OBJ_EXT): /usr/include/sys/stdint.h
hash$(OBJ_EXT): /usr/include/sys/time.h
hash$(OBJ_EXT): /usr/include/sys/times.h
hash$(OBJ_EXT): /usr/include/sys/timespec.h
hash$(OBJ_EXT): /usr/include/sys/types.h
hash$(OBJ_EXT): /usr/include/time.h
hash$(OBJ_EXT): EXTERN.h
hash$(OBJ_EXT): a2p.h
hash$(OBJ_EXT): hash.c
hash$(OBJ_EXT): hash.h
hash$(OBJ_EXT): str.h
hash$(OBJ_EXT): util.h
str$(OBJ_EXT): ../config.h
str$(OBJ_EXT): ../handy.h
str$(OBJ_EXT): /usr/include/_ctype.h
str$(OBJ_EXT): /usr/include/ctype.h
str$(OBJ_EXT): /usr/include/inttypes.h
str$(OBJ_EXT): /usr/include/machine/_inttypes.h
str$(OBJ_EXT): /usr/include/machine/_limits.h
str$(OBJ_EXT): /usr/include/machine/_stdint.h
str$(OBJ_EXT): /usr/include/machine/_types.h
str$(OBJ_EXT): /usr/include/machine/endian.h
str$(OBJ_EXT): /usr/include/math.h
str$(OBJ_EXT): /usr/include/runetype.h
str$(OBJ_EXT): /usr/include/stdio.h
str$(OBJ_EXT): /usr/include/stdlib.h
str$(OBJ_EXT): /usr/include/string.h
str$(OBJ_EXT): /usr/include/strings.h
str$(OBJ_EXT): /usr/include/sys/_null.h
str$(OBJ_EXT): /usr/include/sys/_pthreadtypes.h
str$(OBJ_EXT): /usr/include/sys/_sigset.h
str$(OBJ_EXT): /usr/include/sys/_timeval.h
str$(OBJ_EXT): /usr/include/sys/_types.h
str$(OBJ_EXT): /usr/include/sys/cdefs.h
str$(OBJ_EXT): /usr/include/sys/select.h
str$(OBJ_EXT): /usr/include/sys/stdint.h
str$(OBJ_EXT): /usr/include/sys/time.h
str$(OBJ_EXT): /usr/include/sys/times.h
str$(OBJ_EXT): /usr/include/sys/timespec.h
str$(OBJ_EXT): /usr/include/sys/types.h
str$(OBJ_EXT): /usr/include/time.h
str$(OBJ_EXT): EXTERN.h
str$(OBJ_EXT): a2p.h
str$(OBJ_EXT): hash.h
str$(OBJ_EXT): str.c
str$(OBJ_EXT): str.h
str$(OBJ_EXT): util.h
util$(OBJ_EXT): ../config.h
util$(OBJ_EXT): ../handy.h
util$(OBJ_EXT): /usr/include/_ctype.h
util$(OBJ_EXT): /usr/include/ctype.h
util$(OBJ_EXT): /usr/include/inttypes.h
util$(OBJ_EXT): /usr/include/machine/_inttypes.h
util$(OBJ_EXT): /usr/include/machine/_limits.h
util$(OBJ_EXT): /usr/include/machine/_stdint.h
util$(OBJ_EXT): /usr/include/machine/_types.h
util$(OBJ_EXT): /usr/include/machine/endian.h
util$(OBJ_EXT): /usr/include/math.h
util$(OBJ_EXT): /usr/include/runetype.h
util$(OBJ_EXT): /usr/include/stdarg.h
util$(OBJ_EXT): /usr/include/stdio.h
util$(OBJ_EXT): /usr/include/stdlib.h
util$(OBJ_EXT): /usr/include/string.h
util$(OBJ_EXT): /usr/include/strings.h
util$(OBJ_EXT): /usr/include/sys/_null.h
util$(OBJ_EXT): /usr/include/sys/_pthreadtypes.h
util$(OBJ_EXT): /usr/include/sys/_sigset.h
util$(OBJ_EXT): /usr/include/sys/_timeval.h
util$(OBJ_EXT): /usr/include/sys/_types.h
util$(OBJ_EXT): /usr/include/sys/cdefs.h
util$(OBJ_EXT): /usr/include/sys/select.h
util$(OBJ_EXT): /usr/include/sys/stdint.h
util$(OBJ_EXT): /usr/include/sys/time.h
util$(OBJ_EXT): /usr/include/sys/times.h
util$(OBJ_EXT): /usr/include/sys/timespec.h
util$(OBJ_EXT): /usr/include/sys/types.h
util$(OBJ_EXT): /usr/include/time.h
util$(OBJ_EXT): EXTERN.h
util$(OBJ_EXT): INTERN.h
util$(OBJ_EXT): a2p.h
util$(OBJ_EXT): hash.h
util$(OBJ_EXT): str.h
util$(OBJ_EXT): util.c
util$(OBJ_EXT): util.h
walk$(OBJ_EXT): ../config.h
walk$(OBJ_EXT): ../handy.h
walk$(OBJ_EXT): /usr/include/_ctype.h
walk$(OBJ_EXT): /usr/include/ctype.h
walk$(OBJ_EXT): /usr/include/inttypes.h
walk$(OBJ_EXT): /usr/include/machine/_inttypes.h
walk$(OBJ_EXT): /usr/include/machine/_limits.h
walk$(OBJ_EXT): /usr/include/machine/_stdint.h
walk$(OBJ_EXT): /usr/include/machine/_types.h
walk$(OBJ_EXT): /usr/include/machine/endian.h
walk$(OBJ_EXT): /usr/include/math.h
walk$(OBJ_EXT): /usr/include/runetype.h
walk$(OBJ_EXT): /usr/include/stdio.h
walk$(OBJ_EXT): /usr/include/stdlib.h
walk$(OBJ_EXT): /usr/include/string.h
walk$(OBJ_EXT): /usr/include/strings.h
walk$(OBJ_EXT): /usr/include/sys/_null.h
walk$(OBJ_EXT): /usr/include/sys/_pthreadtypes.h
walk$(OBJ_EXT): /usr/include/sys/_sigset.h
walk$(OBJ_EXT): /usr/include/sys/_timeval.h
walk$(OBJ_EXT): /usr/include/sys/_types.h
walk$(OBJ_EXT): /usr/include/sys/cdefs.h
walk$(OBJ_EXT): /usr/include/sys/select.h
walk$(OBJ_EXT): /usr/include/sys/stdint.h
walk$(OBJ_EXT): /usr/include/sys/time.h
walk$(OBJ_EXT): /usr/include/sys/times.h
walk$(OBJ_EXT): /usr/include/sys/timespec.h
walk$(OBJ_EXT): /usr/include/sys/types.h
walk$(OBJ_EXT): /usr/include/time.h
walk$(OBJ_EXT): EXTERN.h
walk$(OBJ_EXT): a2p.h
walk$(OBJ_EXT): hash.h
walk$(OBJ_EXT): str.h
walk$(OBJ_EXT): util.h
walk$(OBJ_EXT): walk.c
cflags: cflags.SH ../config.sh ; /bin/sh cflags.SH
# WARNING: Put nothing here or make depend will gobble it up!
