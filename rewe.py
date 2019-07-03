import itertools

class Rewe:
    def __init__(self):
        self.verb=False
        self.konto={}
        for eintrag in (('EBK',8000),
                        ('SBK',8010),

                        ('Umsatzerlöse',5000),

                        ('GuV',8020),

                        ('Vorsteuer',2600),
                        ('Umsatzsteuer',4800),
                        
                        ('Rohstoffe',2000),
                        ('Aufwendungen Rohstoffe',6000),
                        ('Bestandsveränderungen',5200),
                        ('Fertige Erzeugnisse',2200),
                        
                        ('Forderungen',2400),
                        ('Verbindlichkeiten',4400),
                        ('VerbKredit',4200),
                        ('Bank',2800),
                        ('Kasse',2880),
                        ('Privat',3001),
                        
                        ('BGA',870),
                        ('TAM',700),
                        ('Eigenkapital',3000)
                        ):
            name,klasse=eintrag
            self.konto[name]={'klasse':klasse,'soll':[],'haben':[]}
        #print(self.konto)
        #exit()

    def verbose(self,verbose):
        self.verb=verbose
        
    def buchen(self,von,an,betrag,vst=0,ust=0):
        if von not in self.konto:
            print('Konto {} existiert nicht!'.format(von))
            exit()
        if an not in self.konto:
            print('Konto {} existiert nicht!'.format(an))
            exit()
        vonbetrag=betrag
        anbetrag=betrag

        if vst>0:
            steuer=vonbetrag*vst/100
            anbetrag=vonbetrag+steuer
            if self.verbose:
                print('+-------------------------------+-------------+-------------+')
                print('| {:04} {:24.24} | {:11.2f} |             |'.format(self.konto[von]['klasse'],von,vonbetrag))
                print('| 2600 {:24.24} | {:11.2f} |             |'.format('Vorsteuer',steuer))
                print('| an {:04} {:21.21} |             | {:11.2f} |'.format(self.konto[an]['klasse'],an,anbetrag))
                print('+-------------------------------+-------------+-------------+')
            self.konto['Vorsteuer']['soll'].append((an,steuer))
        elif ust>0:
            steuer=anbetrag*ust/100
            vonbetrag=anbetrag+steuer
            if self.verbose:
                print('+-------------------------------+-------------+-------------+')
                print('| {:04} {:24.24} | {:11.2f} |             |'.format(self.konto[von]['klasse'],von,vonbetrag))
                print('| an {:04} {:21.21} |             | {:11.2f} |'.format(self.konto[an]['klasse'],an,anbetrag))
                print('|    4800 {:21.21} |             | {:11.2f} |'.format('Umsatzsteuer',steuer))
                print('+-------------------------------+-------------+-------------+')
            self.konto['Umsatzsteuer']['haben'].append((von,steuer))
        else:
            if self.verbose:
                print('+-------------------------------+-------------+-------------+')
                print('| {:04} {:24.24} | {:11.2f} |             |'.format(self.konto[von]['klasse'],von,vonbetrag))
                print('| an {:04} {:21.21} |             | {:11.2f} |'.format(self.konto[an]['klasse'],an,anbetrag))
                print('+-------------------------------+-------------+-------------+')
        if self.verbose:
            print()
        self.konto[von]['soll'].append((an,vonbetrag))
        self.konto[an]['haben'].append((von,anbetrag))

    def zeigeKonto(self,name):
        if name in self.konto:
            #print(name)
            try:
                kname='{:04} {}'.format(self.konto[name]['klasse'],name)
            except:
                print(name)
                exit()
            print(' S {:^51} H'.format(kname))
            print('----------------------------+----------------------------')
            ssoll=[]
            shaben=[]
            for ziel,soll in self.konto[name]['soll']:
                ssoll.append('{:14.14} {:11.2f}'.format(ziel,soll))
            for ziel,haben in self.konto[name]['haben']:
                shaben.append('{:14.14} {:11.2f}'.format(ziel,haben))
            for links,rechts in itertools.zip_longest(ssoll,shaben):
                if links==None:
                    links='                          '
                if rechts==None:
                    rechts=''
                print(' {} | {}'.format(links,rechts))
            if self.saldo(name)>0:
                print('Saldo: {:11.2f}'.format(self.saldo(name)))
            print()

    def soll(self,name):
        summe_soll=0
        for ziel,soll in self.konto[name]['soll']:
            summe_soll+=soll
        return summe_soll
    
    def haben(self,name):
        summe_haben=0
        for ziel,haben in self.konto[name]['haben']:
            summe_haben+=haben
        return summe_haben
    
    def saldo(self,name):
        return abs(self.soll(name)-self.haben(name))

    def kontoAbschließen(self,name,ziel):
        if self.haben(name)>self.soll(name):
            self.buchen(name,ziel,self.saldo(name))
        elif self.soll(name)>self.haben(name):
            self.buchen(ziel,name,self.saldo(name))
        else:
            if self.verbose:
                print('-> Keine Buchung.')
            
    def abschluß(self):
        vstsaldo=self.saldo('Vorsteuer')
        ustsaldo=self.saldo('Umsatzsteuer')
        saldo=abs(vstsaldo-ustsaldo)


        if self.verbose:
            print('Vorsteuerüberhang/Umsatzsteuerzahllast berechnen')
        #Umsatzsteuerzahllast
        if ustsaldo>vstsaldo:
            if vstsaldo>0:
                self.buchen('Umsatzsteuer','Vorsteuer',vstsaldo)
            self.buchen('Umsatzsteuer','SBK',self.saldo('Umsatzsteuer'))
        #Vorsteuerüberhang
        elif vstsaldo>ustsaldo:
            if ustsaldo>0:
                self.buchen('Umsatzsteuer','Vorsteuer',ustsaldo)
            self.buchen('SBK','Vorsteuer',self.saldo('Vorsteuer'))

        #Privat

        if self.verbose:
            print('Privat/EK abschließen')
        self.kontoAbschließen('Privat','Eigenkapital')

        #Erfolg/GuV
        if self.verbose:
            print('Erfolgskonten abschließen')
            print('GuV an Aufwendungen')
        for kto in ['Aufwendungen Rohstoffe']:
            if self.saldo(kto)>0:
                self.buchen('GuV',kto,self.saldo(kto))
        if self.verbose:
            print('Erträge an GuV')
        #Erträge an GuV
        for kto in ['Umsatzerlöse']:
            if self.saldo(kto)>0:
                self.buchen(kto,'GuV',self.saldo(kto))

        #GuV/EK
        if self.verbose:
            print('GuV über Eigenkapital abschließen')
        self.kontoAbschließen('GuV','Eigenkapital')

        #Bestand/SBK
        if self.verbose:
            print('Bestandskonten')
            print('SBK an Aktivkonten')
        for kto in ['Rohstoffe','BGA','TAM','Fertige Erzeugnisse',
                    'Forderungen','Kasse']:
            if self.saldo(kto)>0:
                self.buchen('SBK',kto,self.saldo(kto))

        #Bank
        if self.verbose:
            print('Bank abschließen')
        if self.haben('Bank')>self.soll('Bank'):
            self.buchen('Bank','VerbKredit',self.saldo('Bank'))
        elif self.haben('Bank')<self.soll('Bank'):
            self.buchen('SBK','Bank',self.saldo('Bank'))
            
        #Passiv an SBK
        if self.verbose:
            print('Passiv an SBK')
        for kto in ['Verbindlichkeiten','VerbKredit']:
            if self.saldo(kto)>0:
                self.buchen(kto,'SBK',self.saldo(kto))

        #EK/SBK
        if self.verbose:
            print('Eigenkapital über SBK abschließen')
        self.kontoAbschließen('Eigenkapital','SBK')

    def zeigeAlleKonten(self):
        print('Kontenübersicht:')
        for name in self.konto.keys():
            if self.soll(name)>0 or self.haben(name)>0:
                self.zeigeKonto(name)

if __name__=='__main__':
    r=Rewe()
    r.verbose(True)
    
    r.buchen('EBK','Eigenkapital',2500)
    r.buchen('Bank','EBK',2500)
    r.buchen('Rohstoffe','Bank',1000,vst=19)
    r.buchen('Aufwendungen Rohstoffe','Rohstoffe',1000)
    r.buchen('Forderungen','Umsatzerlöse',2000,ust=19)
    r.buchen('Bank','Forderungen',2380)
    r.buchen('Privat','Bank',100)

    r.abschluß()

    r.zeigeAlleKonten()
