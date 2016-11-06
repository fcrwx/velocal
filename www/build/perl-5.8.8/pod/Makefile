# pod/Makefile
# This file is derived from pod/Makefile.SH.  Any changes made here will
# be lost the next time you run Configure.

POD = perl.pod perl5004delta.pod perl5005delta.pod perl561delta.pod perl56delta.pod perl570delta.pod perl571delta.pod perl572delta.pod perl573delta.pod perl581delta.pod perl582delta.pod perl583delta.pod perl584delta.pod perl585delta.pod perl586delta.pod perl587delta.pod perl588delta.pod perl58delta.pod perlaix.pod perlamiga.pod perlapi.pod perlapio.pod perlapollo.pod perlartistic.pod perlbeos.pod perlbook.pod perlboot.pod perlbot.pod perlbs2000.pod perlcall.pod perlce.pod perlcheat.pod perlclib.pod perlcn.pod perlcompile.pod perlcygwin.pod perldata.pod perldbmfilter.pod perldebguts.pod perldebtut.pod perldebug.pod perldelta.pod perldgux.pod perldiag.pod perldoc.pod perldos.pod perldsc.pod perlebcdic.pod perlembed.pod perlepoc.pod perlfaq.pod perlfaq1.pod perlfaq2.pod perlfaq3.pod perlfaq4.pod perlfaq5.pod perlfaq6.pod perlfaq7.pod perlfaq8.pod perlfaq9.pod perlfilter.pod perlfork.pod perlform.pod perlfreebsd.pod perlfunc.pod perlglossary.pod perlgpl.pod perlguts.pod perlhack.pod perlhist.pod perlhpux.pod perlhurd.pod perlintern.pod perlintro.pod perliol.pod perlipc.pod perlirix.pod perljp.pod perlko.pod perllexwarn.pod perllinux.pod perllocale.pod perllol.pod perlmachten.pod perlmacos.pod perlmacosx.pod perlmint.pod perlmod.pod perlmodinstall.pod perlmodlib.pod perlmodstyle.pod perlmpeix.pod perlnetware.pod perlnewmod.pod perlnumber.pod perlobj.pod perlop.pod perlopenbsd.pod perlopentut.pod perlos2.pod perlos390.pod perlos400.pod perlothrtut.pod perlpacktut.pod perlplan9.pod perlpod.pod perlpodspec.pod perlport.pod perlqnx.pod perlre.pod perlref.pod perlreftut.pod perlrequick.pod perlreref.pod perlretut.pod perlrun.pod perlsec.pod perlsolaris.pod perlstyle.pod perlsub.pod perlsyn.pod perlthrtut.pod perltie.pod perltoc.pod perltodo.pod perltooc.pod perltoot.pod perltrap.pod perltru64.pod perltw.pod perlunicode.pod perluniintro.pod perlutil.pod perluts.pod perlvar.pod perlvmesa.pod perlvms.pod perlvos.pod perlwin32.pod perlxs.pod perlxstut.pod

MAN = perl.man perl5004delta.man perl5005delta.man perl561delta.man perl56delta.man perl570delta.man perl571delta.man perl572delta.man perl573delta.man perl581delta.man perl582delta.man perl583delta.man perl584delta.man perl585delta.man perl586delta.man perl587delta.man perl588delta.man perl58delta.man perlaix.man perlamiga.man perlapi.man perlapio.man perlapollo.man perlartistic.man perlbeos.man perlbook.man perlboot.man perlbot.man perlbs2000.man perlcall.man perlce.man perlcheat.man perlclib.man perlcn.man perlcompile.man perlcygwin.man perldata.man perldbmfilter.man perldebguts.man perldebtut.man perldebug.man perldelta.man perldgux.man perldiag.man perldoc.man perldos.man perldsc.man perlebcdic.man perlembed.man perlepoc.man perlfaq.man perlfaq1.man perlfaq2.man perlfaq3.man perlfaq4.man perlfaq5.man perlfaq6.man perlfaq7.man perlfaq8.man perlfaq9.man perlfilter.man perlfork.man perlform.man perlfreebsd.man perlfunc.man perlglossary.man perlgpl.man perlguts.man perlhack.man perlhist.man perlhpux.man perlhurd.man perlintern.man perlintro.man perliol.man perlipc.man perlirix.man perljp.man perlko.man perllexwarn.man perllinux.man perllocale.man perllol.man perlmachten.man perlmacos.man perlmacosx.man perlmint.man perlmod.man perlmodinstall.man perlmodlib.man perlmodstyle.man perlmpeix.man perlnetware.man perlnewmod.man perlnumber.man perlobj.man perlop.man perlopenbsd.man perlopentut.man perlos2.man perlos390.man perlos400.man perlothrtut.man perlpacktut.man perlplan9.man perlpod.man perlpodspec.man perlport.man perlqnx.man perlre.man perlref.man perlreftut.man perlrequick.man perlreref.man perlretut.man perlrun.man perlsec.man perlsolaris.man perlstyle.man perlsub.man perlsyn.man perlthrtut.man perltie.man perltoc.man perltodo.man perltooc.man perltoot.man perltrap.man perltru64.man perltw.man perlunicode.man perluniintro.man perlutil.man perluts.man perlvar.man perlvmesa.man perlvms.man perlvos.man perlwin32.man perlxs.man perlxstut.man

# no perltoc.html
HTML = perl.html perl5004delta.html perl5005delta.html perl561delta.html perl56delta.html perl570delta.html perl571delta.html perl572delta.html perl573delta.html perl581delta.html perl582delta.html perl583delta.html perl584delta.html perl585delta.html perl586delta.html perl587delta.html perl588delta.html perl58delta.html perlaix.html perlamiga.html perlapi.html perlapio.html perlapollo.html perlartistic.html perlbeos.html perlbook.html perlboot.html perlbot.html perlbs2000.html perlcall.html perlce.html perlcheat.html perlclib.html perlcn.html perlcompile.html perlcygwin.html perldata.html perldbmfilter.html perldebguts.html perldebtut.html perldebug.html perldelta.html perldgux.html perldiag.html perldoc.html perldos.html perldsc.html perlebcdic.html perlembed.html perlepoc.html perlfaq.html perlfaq1.html perlfaq2.html perlfaq3.html perlfaq4.html perlfaq5.html perlfaq6.html perlfaq7.html perlfaq8.html perlfaq9.html perlfilter.html perlfork.html perlform.html perlfreebsd.html perlfunc.html perlglossary.html perlgpl.html perlguts.html perlhack.html perlhist.html perlhpux.html perlhurd.html perlintern.html perlintro.html perliol.html perlipc.html perlirix.html perljp.html perlko.html perllexwarn.html perllinux.html perllocale.html perllol.html perlmachten.html perlmacos.html perlmacosx.html perlmint.html perlmod.html perlmodinstall.html perlmodlib.html perlmodstyle.html perlmpeix.html perlnetware.html perlnewmod.html perlnumber.html perlobj.html perlop.html perlopenbsd.html perlopentut.html perlos2.html perlos390.html perlos400.html perlothrtut.html perlpacktut.html perlplan9.html perlpod.html perlpodspec.html perlport.html perlqnx.html perlre.html perlref.html perlreftut.html perlrequick.html perlreref.html perlretut.html perlrun.html perlsec.html perlsolaris.html perlstyle.html perlsub.html perlsyn.html perlthrtut.html perltie.html  perltodo.html perltooc.html perltoot.html perltrap.html perltru64.html perltw.html perlunicode.html perluniintro.html perlutil.html perluts.html perlvar.html perlvmesa.html perlvms.html perlvos.html perlwin32.html perlxs.html perlxstut.html

TEX  = perl.tex perl5004delta.tex perl5005delta.tex perl561delta.tex perl56delta.tex perl570delta.tex perl571delta.tex perl572delta.tex perl573delta.tex perl581delta.tex perl582delta.tex perl583delta.tex perl584delta.tex perl585delta.tex perl586delta.tex perl587delta.tex perl588delta.tex perl58delta.tex perlaix.tex perlamiga.tex perlapi.tex perlapio.tex perlapollo.tex perlartistic.tex perlbeos.tex perlbook.tex perlboot.tex perlbot.tex perlbs2000.tex perlcall.tex perlce.tex perlcheat.tex perlclib.tex perlcn.tex perlcompile.tex perlcygwin.tex perldata.tex perldbmfilter.tex perldebguts.tex perldebtut.tex perldebug.tex perldelta.tex perldgux.tex perldiag.tex perldoc.tex perldos.tex perldsc.tex perlebcdic.tex perlembed.tex perlepoc.tex perlfaq.tex perlfaq1.tex perlfaq2.tex perlfaq3.tex perlfaq4.tex perlfaq5.tex perlfaq6.tex perlfaq7.tex perlfaq8.tex perlfaq9.tex perlfilter.tex perlfork.tex perlform.tex perlfreebsd.tex perlfunc.tex perlglossary.tex perlgpl.tex perlguts.tex perlhack.tex perlhist.tex perlhpux.tex perlhurd.tex perlintern.tex perlintro.tex perliol.tex perlipc.tex perlirix.tex perljp.tex perlko.tex perllexwarn.tex perllinux.tex perllocale.tex perllol.tex perlmachten.tex perlmacos.tex perlmacosx.tex perlmint.tex perlmod.tex perlmodinstall.tex perlmodlib.tex perlmodstyle.tex perlmpeix.tex perlnetware.tex perlnewmod.tex perlnumber.tex perlobj.tex perlop.tex perlopenbsd.tex perlopentut.tex perlos2.tex perlos390.tex perlos400.tex perlothrtut.tex perlpacktut.tex perlplan9.tex perlpod.tex perlpodspec.tex perlport.tex perlqnx.tex perlre.tex perlref.tex perlreftut.tex perlrequick.tex perlreref.tex perlretut.tex perlrun.tex perlsec.tex perlsolaris.tex perlstyle.tex perlsub.tex perlsyn.tex perlthrtut.tex perltie.tex perltoc.tex perltodo.tex perltooc.tex perltoot.tex perltrap.tex perltru64.tex perltw.tex perlunicode.tex perluniintro.tex perlutil.tex perluts.tex perlvar.tex perlvmesa.tex perlvms.tex perlvos.tex perlwin32.tex perlxs.tex perlxstut.tex  

# The following is used to include the current directory in
# the dynamic loader path you are building a shared libperl.
LDLIBPTH = 


CONVERTERS = pod2html pod2latex pod2man pod2text checkpods \
		pod2usage podchecker podselect

HTMLROOT = /	# Change this to fix cross-references in HTML
POD2HTML = pod2html \
	    --htmlroot=$(HTMLROOT) \
	    --podroot=.. --podpath=pod:lib:ext:vms \
	    --libpods=perlfunc:perlguts:perlvar:perlrun:perlop

PERL = ../miniperl
PERLILIB = $(PERL) -I../lib
REALPERL = ../perl

all: $(CONVERTERS) man

converters: $(CONVERTERS)

regen_pods: perlmodlib.pod toc

perltoc.pod:	buildtoc

man:	pod2man $(MAN)

html:	pod2html $(HTML)

tex:	pod2latex $(TEX)

toc perltoc.pod:	buildtoc
	$(PERLILIB) buildtoc --build-toc

.SUFFIXES: .pm .pod

.SUFFIXES: .man

.pm.man:     pod2man
	$(PERL) -I../lib pod2man $*.pm >$*.man

.pod.man:     pod2man
	$(PERL) -I../lib pod2man $*.pod >$*.man

.SUFFIXES: .html

.pm.html:    pod2html
	$(PERL) -I../lib $(POD2HTML) --infile=$*.pm --outfile=$*.html

.pod.html:    pod2html
	$(PERL) -I../lib $(POD2HTML) --infile=$*.pod --outfile=$*.html

.SUFFIXES: .tex

.pm.tex: pod2latex
	$(PERL) -I../lib pod2latex $*.pm

.pod.tex: pod2latex
	$(PERL) -I../lib pod2latex $*.pod

clean:
	rm -f $(MAN)
	rm -f $(HTML)
	rm -f $(TEX)
	rm -f pod2html-*cache
	rm -f *.aux *.log *.exe

realclean:	clean
	rm -f $(CONVERTERS)

distclean:	realclean

veryclean:	distclean
	-rm -f *~ *.orig

check:	checkpods
	@echo "checking..."; \
	$(PERL) -I../lib checkpods $(POD)

# Dependencies.
pod2latex:	pod2latex.PL ../lib/Config.pm
	$(LDLIBPTH) $(PERL) -I../lib pod2latex.PL

pod2html:	pod2html.PL ../lib/Config.pm
	$(LDLIBPTH) $(PERL) -I ../lib pod2html.PL

pod2man:	pod2man.PL ../lib/Config.pm
	$(LDLIBPTH) $(PERL) -I ../lib pod2man.PL

pod2text:	pod2text.PL ../lib/Config.pm
	$(LDLIBPTH) $(PERL) -I ../lib pod2text.PL

checkpods:	checkpods.PL ../lib/Config.pm
	$(LDLIBPTH) $(PERL) -I ../lib checkpods.PL

pod2usage:	pod2usage.PL ../lib/Config.pm
	$(PERL) -I ../lib pod2usage.PL

podchecker:	podchecker.PL ../lib/Config.pm
	$(PERL) -I ../lib podchecker.PL

podselect:	podselect.PL ../lib/Config.pm
	$(PERL) -I ../lib podselect.PL

perlmodlib.pod:	$(PERL) perlmodlib.PL ../MANIFEST
	rm -f perlmodlib.pod
	$(PERL) -I ../lib perlmodlib.PL

compile: all
	$(REALPERL) -I../lib ../utils/perlcc -I .. -L .. -o pod2latex.exe pod2latex -log ../compilelog
	$(REALPERL) -I../lib ../utils/perlcc -I .. -L .. -o pod2man.exe pod2man -log ../compilelog
	$(REALPERL) -I../lib ../utils/perlcc -I .. -L .. -o pod2text.exe pod2text -log ../compilelog
	$(REALPERL) -I../lib ../utils/perlcc -I .. -L .. -o checkpods.exe checkpods -log ../compilelog

