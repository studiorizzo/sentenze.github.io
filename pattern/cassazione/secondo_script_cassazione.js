/**
 * ESTRATTORE CASSAZIONE - VERSIONE ESAUSTIVA COMPLETA
 * 
 * Basato su analisi esaustiva di 4.956 termini reali da JSON MEF e Giustizia Tributaria
 * TOTALE QUERY: 3.653
 * 
 * ISTRUZIONI:
 * 1. Apri https://www.italgiure.giustizia.it/sncass/
 * 2. Apri Console (F12 > Console)
 * 3. Incolla questo script e premi Invio
 * 4. Aspetta 15-20 minuti (3653 query con delay 300ms)
 * 5. Scarica automaticamente i file JSON
 */

(async function() {
    console.log('='.repeat(70));
    console.log('🎯 ESTRATTORE CASSAZIONE - VERSIONE ESAUSTIVA');
    console.log('='.repeat(70));
    
    const BASE_URL = window.location.origin + '/sncass/';
    const SOLR_ENDPOINT = 'isapi/hc.dll/sn.solr/sn-collection/select?app.suggester';
    const DELAY = 300;
    
    console.log(`\nBase URL: ${BASE_URL}`);
    console.log(`Endpoint: ${SOLR_ENDPOINT}`);
    
    // ========================================================================
    // DATI DA ANALISI ESAUSTIVA (incorporati)
    // ========================================================================
    
    const ANALYSIS_DATA = 
{"single_chars":["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9"],"bigrams":["'a","'e","'i","'o","'u","aa","ab","ac","ad","ae","af","ag","ai","al","am","an","ao","ap","ar","as","at","au","av","az","ba","bb","bc","be","bi","bl","bo","br","bu","ca","cc","ce","cf","ch","ci","ck","cl","cn","co","cp","cq","cr","ct","cu","cy","d'","da","dd","de","dg","di","do","dp","dr","du","ea","eb","ec","ed","ee","ef","eg","ei","el","em","en","eo","ep","eq","er","es","et","eu","ev","ew","ex","ez","fa","fc","fe","ff","fi","fl","fo","fr","fu","ga","ge","gg","gh","gi","gl","gm","gn","go","gp","gr","gu","ha","he","hi","ia","ib","ic","id","ie","if","ig","il","im","in","io","ip","iq","ir","is","it","iu","iv","iz","ià","ke","ki","l'","la","lb","lc","ld","le","lf","lg","li","ll","lm","lo","ls","lt","lu","lv","ly","ma","mb","me","mi","mm","mn","mo","mp","ms","mu","na","nc","nd","ne","nf","ng","ni","nk","nl","nn","no","nq","ns","nt","nu","nv","nz","oa","ob","oc","od","oe","of","og","oi","ol","om","on","oo","op","or","os","ot","ou","ov","oz","pa","pe","pi","pl","po","pp","pr","ps","pt","pu","pz","qu","ra","rb","rc","rd","re","rf","rg","ri","rk","rm","rn","ro","rp","rr","rs","rt","ru","rv","rz","sa","sc","sd","se","sf","sg","sh","si","sk","sl","sm","so","sp","ss","st","su","sv","sw","ta","tc","te","tf","th","ti","to","tr","tt","tu","tà","ua","ub","uc","ud","ue","uf","ug","ui","ul","um","un","uo","up","ur","us","ut","uz","va","ve","vi","vo","vr","vu","vv","wa","ws","xt","za","ze","zi","zo","zz"],"trigrams":["'ac","'af","'ag","'al","'am","'an","'ap","'at","'au","'av","'az","'en","'es","'im","'in","'is","'it","'ob","'oc","'on","'op","'or","'uf","'un","'us","aam","aba","abb","abi","abo","abu","aca","acc","ace","aci","ack","aco","acp","acq","acy","ada","add","ade","adi","ado","adr","aer","aes","afe","aff","afi","afo","aga","age","agg","agi","agl","agn","ago","agr","aib","aio","aiu","ala","alb","alc","ald","ale","ali","all","alm","alo","als","alt","alu","aly","ama","amb","ame","ami","amm","amn","amp","ams","ana","anc","and","ane","ang","ani","ank","ann","ano","ans","ant","anu","anz","aod","aor","apa","ape","api","app","ara","arb","arc","ard","are","arg","ari","ark","arm","arn","aro","arr","ars","art","arz","asa","asc","ase","asf","asi","asm","aso","asp","ass","ast","ata","atc","ate","ati","ato","atr","att","atu","aud","aul","aum","aun","aur","aus","aut","auz","ava","ave","avi","avo","avv","azi","azo","azz","bac","bag","bal","ban","bar","bas","bat","bba","bbi","bbl","bbo","bbr","bbu","bce","bel","ben","ber","bia","bie","big","bil","bin","bio","bir","bis","bit","biz","bli","blo","bol","bon","bor","bot","bre","bri","bro","bue","bui","bul","buo","bur","bus","but","buz","cab","cac","cad","caf","cag","cal","cam","can","cap","car","cas","cat","cau","cav","caz","cca","cce","cch","cci","ccl","cco","ccu","ced","cel","cen","cer","ces","cet","ceu","cev","cfc","che","chi","cia","cib","cic","cid","cie","cif","cil","cim","cin","cio","cip","cir","cis","cit","civ","ciz","cke","cla","cle","cli","clu","cni","cno","coa","cod","coe","cof","col","com","con","coo","cop","cor","cos","cot","cou","cov","cqu","cre","cri","cro","cui","cul","cum","cun","cuo","cup","cur","cus","cut","cuz","d'a","d'e","d'i","d'o","d'u","dac","dag","dal","dam","dan","dar","dat","dav","daz","ddi","deb","dec","ded","def","deg","dei","del","dem","den","deo","dep","der","des","det","dge","dia","dic","did","die","dif","dig","dil","dim","din","dio","dip","dir","dis","dit","div","diz","doc","dog","dol","dom","don","dop","dot","dov","doz","dpr","dra","dri","dro","dua","duc","due","dui","dul","dum","dur","dus","dut","duz","eal","eam","eas","eat","ebi","ebr","eca","ecc","ece","eci","ecl","ecn","eco","ecr","ecu","eda","edd","ede","edi","edo","edu","efe","eff","efi","efo","efu","ega","egg","egh","egi","egl","egn","ego","egr","egu","eic","eig","ein","eit","eiz","ela","ele","eli","ell","elt","elu","ema","emb","eme","emi","emo","emp","ena","enc","end","ene","enf","eni","enn","eno","ens","ent","enu","enz","eog","eol","epa","epe","epi","epo","epu","equ","era","erb","erc","erd","ere","erf","erg","eri","erm","ern","ero","erp","err","ers","ert","erv","erz","esa","esc","ese","esi","eso","esp","ess","est","esu","eta","ete","eti","eto","etr","ett","età","eur","eus","eut","eva","eve","evi","evo","evu","ews","ext","ezi","ezz","fab","fac","fal","fam","far","fas","fat","fau","fav","fea","fed","fer","fes","fet","fez","ffa","ffe","ffi","ffu","fia","fic","fid","fig","fil","fin","fis","fit","fiu","flo","flu","fog","fon","for","fra","fre","fro","fru","fum","fun","fuo","fur","fus","gag","gal","gam","gan","gar","gas","gat","gaz","ged","gen","geo","ges","get","gev","gge","ggi","ggr","ghe","ghi","gia","gib","gic","gie","gil","gim","gin","gio","gir","gis","git","giu","gli","glo","gma","gna","gni","gno","god","gol","gor","gov","goz","gpl","gra","gre","gri","gru","gua","gue","gui","han","har","hed","her","het","hia","hie","hig","him","hin","hio","hit","hiu","hiv","iaa","iab","iac","iag","ial","iam","ian","iap","iar","ias","iat","iaz","ibe","ibi","ibo","ibr","ibu","ica","icc","ice","ich","ici","ick","icl","ico","icr","icu","ida","ide","idi","ido","idr","idu","ieg","iel","ien","iep","ier","ies","iet","iev","ife","iff","ifi","iga","ige","igh","igi","igl","igm","ign","igo","igr","igu","ila","ile","ili","ill","ilo","ilu","ima","imb","ime","imi","imm","imo","imp","imu","ina","inc","ind","ine","inf","ing","ini","inn","ino","inq","ins","int","inu","inv","inz","ioc","iod","iog","iol","ion","ior","ios","ipa","ipe","ipi","ipl","ipo","ipp","ipr","ipt","iqu","ira","irc","ire","iri","iro","irp","irr","irs","isa","isc","isd","ise","isg","isi","isl","ism","iso","isp","iss","ist","isu","ita","ite","iti","ito","itr","itt","itu","ità","iud","iug","iun","iur","ius","iut","iva","ive","ivi","ivo","izi","izz","ker","ket","kil","l'a","l'e","l'i","l'o","l'u","lab","lac","laf","lag","lam","lan","lar","las","lat","lau","lav","laz","lbo","lci","lco","ldo","lea","lec","lef","leg","lem","len","ler","les","let","lev","lez","lfo","lia","lib","lic","lid","lie","lif","lig","lil","lim","lin","lio","liq","lis","lit","liv","liz","ll'","lla","lle","lli","llo","llu","lme","loa","lob","loc","log","lom","lon","lor","los","lot","lsa","lse","lta","lte","lti","ltr","ltu","ltà","luc","lue","lug","lul","lum","lun","luo","lup","lur","lus","lut","luz","mac","mad","maf","mag","mal","mam","man","map","mar","mas","mat","maz","mba","mbi","mbo","mbr","mbu","mec","med","mef","mel","mem","men","mer","mes","met","mez","mia","mic","mif","mig","mil","min","mio","mis","mit","mma","mme","mmi","mmo","mni","mob","mod","mol","mom","mon","mor","mot","mov","moz","mpa","mpe","mpi","mpl","mpo","mpr","mpu","mul","mun","mut","nab","nac","nad","nag","nal","nam","nan","nap","nar","nat","nau","nav","naz","nca","nce","nch","nci","ncl","nco","ncr","nda","nde","ndi","ndo","ndu","nea","neb","ned","nee","nef","neg","nei","nel","nen","neo","ner","nes","net","nev","new","nfe","nfi","nfo","nfr","nga","nge","ngi","ngo","ngr","nia","nib","nic","nid","nie","nif","nim","nio","nir","nis","nit","niu","niv","niz","nlu","nna","nne","nni","nno","nnu","nol","nom","non","nop","nor","nos","not","nov","nqu","nsa","nse","nsi","nso","nsu","nta","nte","nti","nto","ntr","ntu","nua","nuc","nul","num","nun","nuo","nus","nut","nuz","nva","nve","nvi","nza","nze","nzi","nzo","oat","oba","obb","obi","oca","occ","oce","och","oci","oco","ocu","oda","ode","odi","odo","odu","oef","ofe","off","ofi","ofo","oga","oge","ogg","ogh","ogi","ogl","ogn","ogo","ogr","ola","ole","olf","oli","oll","olo","olt","olu","oma","omb","ome","omi","omm","omo","omp","omu","ona","onc","ond","one","onf","ong","oni","onl","onn","ono","ons","ont","onu","onv","oob","oop","oor","opa","ope","opi","opo","opp","opr","opz","ora","ord","ore","orf","org","ori","orm","orn","oro","orp","orr","ors","ort","orv","orz","osa","osc","ose","osi","oso","osp","oss","ost","osu","ota","ote","oti","oto","otr","ott","otu","ova","ove","ovi","ovr","ovu","ovv","ozi","pac","pae","pag","pal","pan","par","pas","pat","paz","pea","pec","ped","pef","peg","pel","pen","peo","per","pes","pet","pez","pia","pic","pie","pif","pig","pil","pim","pin","pio","pit","pià","pla","ple","pli","plo","plu","pog","poi","pol","pon","pop","por","pos","pot","ppa","ppe","ppi","ppl","ppo","ppr","ppu","pra","pre","pri","pro","psi","pto","pub","pug","pun","pur","put","pzi","qua","que","qui","quo","rab","rac","rad","raf","rag","rai","ral","ram","ran","rao","rap","rar","ras","rat","rau","rav","raz","rba","rbu","rca","rce","rch","rci","rco","rcu","rda","rdi","rdo","rdu","rea","rec","red","ree","ref","reg","rei","rel","rem","ren","reo","rep","req","rer","res","ret","rev","rez","rfe","rfi","rga","rge","rgh","rgi","rgo","ria","rib","ric","rid","rie","rif","rig","ril","rim","rin","rio","rip","rir","ris","rit","riv","riz","rma","rme","rmi","rmo","rmu","rna","rne","rni","rno","rob","roc","rod","rof","rog","rol","rom","ron","rop","ror","ros","rot","rov","rpe","rpi","rpo","rra","rre","rri","rro","rru","rsa","rse","rsi","rso","rst","rsu","rta","rte","rti","rto","rtu","rui","rum","ruo","rup","rur","rus","rut","ruz","rva","rve","rvi","rza","rzi","sab","sag","sal","sam","san","sap","sar","sat","sav","saz","sca","sce","sch","sci","scl","sco","scr","scu","sdi","sec","sed","see","seg","sel","sem","sen","sep","seq","ser","ses","set","sez","sfe","sfo","sga","sgr","sia","sib","sic","sid","sie","sif","sig","sil","sim","sin","sio","sis","sit","siv","siz","sla","slo","sma","smi","smo","soc","sog","sol","som","son","sop","sor","sos","sot","sov","spa","spe","spl","spo","spr","ssa","sse","ssi","sso","ssu","sta","ste","sti","sto","str","stu","sua","sub","suc","suf","sug","sui","sul","sum","sun","suo","sup","sur","sus","sva","svi","svo","swa","tab","tac","taf","tag","tai","tal","tam","tan","tar","tas","tat","taz","tch","tec","teg","tei","tel","tem","ten","ter","tes","tet","teu","tez","tfr","tia","tib","tic","tie","tif","tig","til","tim","tin","tio","tip","tis","tit","tiv","tiz","toc","tod","tog","tol","tom","ton","top","tor","tos","tot","tra","tre","tri","tro","tru","tta","tte","tti","tto","ttr","ttu","ttà","tua","tub","tud","tue","tui","tun","tuo","tur","tut","tuz","uad","ual","uam","uan","uar","uat","uaz","uba","ubb","ubl","uca","ucc","uci","ucl","udi","udo","uel","uen","uer","ues","uff","ufr","uga","ugl","ugn","uib","uid","uie","uin","uir","uis","uit","uiv","ula","ule","uli","ull","ulo","ult","uma","ume","umi","umo","ump","umu","una","unc","une","ung","uni","unt","unz","uog","uol","uon","uor","uot","uov","upa","upe","upp","ura","urb","ure","uri","uro","urt","usa","usc","use","usi","uso","uss","ust","usu","usv","uta","ute","uti","uto","utt","utu","uzi","vac","val","vam","van","var","vas","vat","vaz","ved","veg","vei","vel","ven","ver","ves","vet","via","vic","vid","vie","vig","vil","vim","vin","vio","vis","vit","viv","viz","voc","vol","vor","vos","vra","vri","vut","vve","vvi","vvo","wap","wsl","xtr","zat","zaz","zia","zie","zin","zio","zon","zot","zza","zzi","zzo"],"words":["aams","abbonamento","abbuoni","abitazione","accertamenti","accertamento","accesso","accise","accordi","acque","acquisti","acquisto","addizionale","addizionali","adempimenti","aeromobili","aeroporti","affissioni","agenzia","agenzie","agevolazioni","agli","agricola","agricoli","agricoltura","aiuti","alcole","aliquote","all'esportazione","all'estero","alla","alle","alloggi","alternatività","altre","altri","ambientale","ambito","amministrativa","amministrative","amministrativi","amministrativo","amministrazione","amministrazioni","amnistia","anagrafe","analisi","annuale","apparecchi","applicazione","area","aree","armi","armonizzate","arti","articolo","artistico","assegnazione","assegno","assicurazioni","assistenza","associazioni","atti","attività","attivo","atto","attribuzioni","automobilistiche","autonoma","autonomo","autorità","aziende","azioni","bagagli","banca","base","benefici","beni","bilancio","bingo","bollo","borsa","calcolo","cali","canone","canoni","capacità","capitale","carico","carta","caso","cassa","catastale","catastali","catasto","causa","cause","cautelari","cauzioni","centrali","centri","certificati","certificazioni","cessazione","cessione","cessioni","circolazione","classamento","classificazione","coatta","coattiva","codice","collaudi","comitato","commerciali","commercio","commissioni","compensazione","compensi","competenza","competenze","complessivo","comunale","comunali","comune","comuni","comunicazione","comunicazioni","comunitari","comunitarie","comunitario","concessionari","concessione","concessioni","conciliazione","concordato","concorrenza","condizioni","condono","conferimento","congruità","consiglio","consolidato","consorzi","consulenza","consulenze","consumatore","consumatori","consumo","contabili","contabilità","contenuto","contenzioso","conti","conto","contratti","contribuente","contribuenti","contributi","contributo","contro","controlli","controllo","controversie","convenzioni","cooperative","cooperazione","corrente","corse","cosap","costruzione","crediti","credito","criteri","culturali","cumulo","d'imposta","d'impresa","d'ufficio","dati","dazi","debito","decadenza","decennale","decentramento","decisioni","decreto","degli","dell'accertamento","dell'imposta","della","delle","dello","demaniali","demanio","denaro","denunce","denuncia","depositi","deposito","determinazione","detrazione","detrazioni","dichiarazione","dichiarazioni","dipendente","diretti","direzioni","diritti","diritto","disciplina","disposizioni","distruzione","diversi","documenti","dogana","doganale","doganali","dogane","domande","domicilio","donazioni","doppia","durata","economica","economici","economico","effetti","elenchi","elettricità","elettronica","energetici","enti","erariale","erariali","esame","esclusione","esecuzione","esenti","esenzioni","esercizio","esigibilità","esonero","esportazione","esportazioni","espropriazione","estere","esteri","estimativi","estimi","estinzione","europea","europeo","fabbricati","fallimento","fattura","fatturazione","fatture","ferrovie","finanza","finanze","finanziamenti","finanziari","finanziaria","finanziarie","finanziario","fini","fiscale","fiscali","fisiche","fissa","fondi","fondiari","fondo","formale","formazione","funzioni","fuori","fusioni","garanzia","generali","gestione","giochi","gioco","giudiziari","giudizio","giuridica","giurisdizione","governative","iciap","illeciti","ilor","immobili","immobiliare","immobiliari","impianti","imponibile","imponibili","importazione","importazioni","impositivo","imposizione","imposta","imposte","impresa","imprese","impugnazione","incremento","indennità","indennizzi","indice","indiretti","informatici","informazioni","ingiunzione","inizio","insegnamento","interesse","interessi","intermediazione","internazionale","internazionali","interpello","interruzione","intracomunitari","intracomunitarie","intrattenimenti","invim","ipotecarie","ippiche","irap","ires","irpef","irpeg","irrogazione","iscrizione","ispezioni","istanza","istituti","istituzione","istruzioni","italia","l'af","lavorazione","lavori","lavoro","legge","libri","licenze","liquidazione","locali","locazione","loro","lotterie","mancato","manutenzione","mappe","marche","mare","materia","materiali","maternità","mediante","mercato","merci","metano","mezzi","minimi","minimo","minori","misura","misure","modalità","modello","momento","monetaria","motivi","mutua","natura","naturali","navi","nazionale","nazionali","negli","negozi","nomina","normale","normativa","norme","notifica","notificazioni","notizie","obbligatoria","obblighi","obbligo","occupazione","omessa","omesso","oneri","operazione","operazioni","opere","opposizione","ordinaria","ordinario","organi","organizzazione","origine","paesi","pagamento","partecipazione","partecipazioni","particolari","partita","parziale","passaggio","passivi","passivo","patrimonio","pecuniarie","pene","pensione","perdite","perfezionamento","periodo","permessi","personale","persone","plafond","plusvalenze","politica","postale","poteri","premio","prescrizione","presentazione","prestazione","prestazioni","prestiti","presunzione","presunzioni","presupposti","presupposto","previdenza","previdenziali","prezzi","principi","principio","privata","private","privati","privilegiata","procedimento","procedura","procedure","processo","prodotti","produzione","professionali","professioni","progetti","programmazione","programmi","proprie","proprietà","proroga","protezione","prova","proventi","provinciale","provvedimenti","provvedimento","pubblica","pubblicazione","pubbliche","pubblici","pubblicità","pubblico","punti","quadro","quota","quote","raccolta","radiodiffusioni","rapporti","rapporto","rappresentanza","rate","reali","redditi","reddito","regime","regimi","regionale","regionali","regioni","registrazione","registri","registro","regole","relative","relativi","rendite","requisiti","residenti","residenza","responsabilità","restituzione","restituzioni","rete","retribuzione","rettifica","ricavi","ricevuta","richiesta","riciclaggio","ricorsi","ricorso","riduzioni","riferimento","rifiuti","rilascio","rimborsi","rimborso","risanamento","riscossione","riserva","risorse","risparmio","ritenuta","ritenute","rivalsa","ruoli","ruolo","salute","sanatoria","sanitarie","sanzioni","scambi","scambio","scommesse","scritture","sedi","segreto","semplificata","semplificazione","sentenza","senza","separata","sequestro","servizi","servizio","settore","sezioni","sicurezza","silenzio","sistema","soci","sociale","società","soggetti","somme","soppressa","soprattassa","sospensione","sostitutiva","sottoscrizione","speciale","speciali","spese","statali","stati","stato","straordinaria","straordinarie","studi","successione","successioni","sugli","sulla","sulle","superficie","sviluppo","tabacchi","tares","tari","tariffa","tariffarie","tariffe","tarsu","tassa","tassazione","tasse","tassi","tasso","tecniche","tecnici","tempo","temporanea","termine","termini","terreni","territori","territoriale","territorio","terzi","tipo","titoli","tosap","traffici","traffico","transito","trascrizione","trasferimenti","trasferimento","trasformazione","trasparenza","trasporti","trasporto","trattamento","trattazione","tributaria","tributario","tributi","tributo","trust","tutela","uffici","ufficiali","unico","unità","urbano","utilizzo","valore","valori","valutazioni","vari","variazione","variazioni","veicoli","vendita","verifiche","versamenti","versamento","viaggiatori","vigilanza","violazioni","visto","zone"],"prefixes":["ex","extra","intra","ultra","post","pre","sub","super","ipo","trans","inter","infra","retro","anti","auto","co","de","dis","in","ri","contra","contro","sotto","sopra","sovra","multi","pluri","mono","uni","bi","tri","meta","para","peri","pro","vice","mini","micro","eco","euro","franco"],"sigle":["(ipt)","(omi)","730","aams","abi","ace","af","agcom","aia","apiet","arera","ariet","arisgam","aspi","ateco","cciaa","cfc","cig","cigs","cnr","cosap","cpc","cpp","ctu","cu","cud","cup","dia","dlgs","dll","dpcm","dpr","durc","enea","eori","f24","fesr","fse","ici","ici)","iciap","icric","ilor","imu","inail","inps","invim","ipt","irap","ires","irpef","irpeg","isa","isee","iuc","iva","ivafe","ivie","mav","mef","mise","mud","mude","nace","naspi","nc","omi","p.a.","pa","pac","patent","pli","pon","por","pra","psr","pvc","rav","red","rid","scia","sdd","sistri","socof","tares","tares)","tari","tarsu","tasi","tonnage","tosap","tuir","unico","v7","vas","via"],"years":["1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"],"articles":["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","52","53","54","55","56","57","58","59","60","61","62","63","64","65","66","67","68","69","70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","92","93","94","95","96","97","98","99","100","101","102","103","104","105","106","107","108","109","110","111","112","113","114","115","116","117","118","119","120","121","122","123","124","125","126","127","128","129","130","131","132","133","134","135","136","137","138","139","140","141","142","143","144","145","146","147","148","149","150","151","152","153","154","155","156","157","158","159","160","161","162","163","164","165","166","167","168","169","170","171","172","173","174","175","176","177","178","179","180","181","182","183","184","185","186","187","188","189","190","191","192","193","194","195","196","197","198","199","200"],"num_letter_combinations":["1 bis","1bis","1-bis","1 ter","1ter","1-ter","1 quater","1quater","1-quater","1 quinquies","1quinquies","1-quinquies","1 sexies","1sexies","1-sexies","1 septies","1septies","1-septies","1 octies","1octies","1-octies","1 novies","1novies","1-novies","1 decies","1decies","1-decies","2 bis","2bis","2-bis","2 ter","2ter","2-ter","2 quater","2quater","2-quater","2 quinquies","2quinquies","2-quinquies","2 sexies","2sexies","2-sexies","2 septies","2septies","2-septies","2 octies","2octies","2-octies","2 novies","2novies","2-novies","2 decies","2decies","2-decies","3 bis","3bis","3-bis","3 ter","3ter","3-ter","3 quater","3quater","3-quater","3 quinquies","3quinquies","3-quinquies","3 sexies","3sexies","3-sexies","3 septies","3septies","3-septies","3 octies","3octies","3-octies","3 novies","3novies","3-novies","3 decies","3decies","3-decies","4 bis","4bis","4-bis","4 ter","4ter","4-ter","4 quater","4quater","4-quater","4 quinquies","4quinquies","4-quinquies","4 sexies","4sexies","4-sexies","4 septies","4septies","4-septies","4 octies","4octies","4-octies","4 novies","4novies","4-novies","4 decies","4decies","4-decies","5 bis","5bis","5-bis","5 ter","5ter","5-ter","5 quater","5quater","5-quater","5 quinquies","5quinquies","5-quinquies","5 sexies","5sexies","5-sexies","5 septies","5septies","5-septies","5 octies","5octies","5-octies","5 novies","5novies","5-novies","5 decies","5decies","5-decies","6 bis","6bis","6-bis","6 ter","6ter","6-ter","6 quater","6quater","6-quater","6 quinquies","6quinquies","6-quinquies","6 sexies","6sexies","6-sexies","6 septies","6septies","6-septies","6 octies","6octies","6-octies","6 novies","6novies","6-novies","6 decies","6decies","6-decies","7 bis","7bis","7-bis","7 ter","7ter","7-ter","7 quater","7quater","7-quater","7 quinquies","7quinquies","7-quinquies","7 sexies","7sexies","7-sexies","7 septies","7septies","7-septies","7 octies","7octies","7-octies","7 novies","7novies","7-novies","7 decies","7decies","7-decies","8 bis","8bis","8-bis","8 ter","8ter","8-ter","8 quater","8quater","8-quater","8 quinquies","8quinquies","8-quinquies","8 sexies","8sexies","8-sexies","8 septies","8septies","8-septies","8 octies","8octies","8-octies","8 novies","8novies","8-novies","8 decies","8decies","8-decies","9 bis","9bis","9-bis","9 ter","9ter","9-ter","9 quater","9quater","9-quater","9 quinquies","9quinquies","9-quinquies","9 sexies","9sexies","9-sexies","9 septies","9septies","9-septies","9 octies","9octies","9-octies","9 novies","9novies","9-novies","9 decies","9decies","9-decies","10 bis","10bis","10-bis","10 ter","10ter","10-ter","10 quater","10quater","10-quater","10 quinquies","10quinquies","10-quinquies","10 sexies","10sexies","10-sexies","10 septies","10septies","10-septies","10 octies","10octies","10-octies","10 novies","10novies","10-novies","10 decies","10decies","10-decies","11 bis","11bis","11-bis","11 ter","11ter","11-ter","11 quater","11quater","11-quater","11 quinquies","11quinquies","11-quinquies","11 sexies","11sexies","11-sexies","11 septies","11septies","11-septies","11 octies","11octies","11-octies","11 novies","11novies","11-novies","11 decies","11decies","11-decies","12 bis","12bis","12-bis","12 ter","12ter","12-ter","12 quater","12quater","12-quater","12 quinquies","12quinquies","12-quinquies","12 sexies","12sexies","12-sexies","12 septies","12septies","12-septies","12 octies","12octies","12-octies","12 novies","12novies","12-novies","12 decies","12decies","12-decies","13 bis","13bis","13-bis","13 ter","13ter","13-ter","13 quater","13quater","13-quater","13 quinquies","13quinquies","13-quinquies","13 sexies","13sexies","13-sexies","13 septies","13septies","13-septies","13 octies","13octies","13-octies","13 novies","13novies","13-novies","13 decies","13decies","13-decies","14 bis","14bis","14-bis","14 ter","14ter","14-ter","14 quater","14quater","14-quater","14 quinquies","14quinquies","14-quinquies","14 sexies","14sexies","14-sexies","14 septies","14septies","14-septies","14 octies","14octies","14-octies","14 novies","14novies","14-novies","14 decies","14decies","14-decies","15 bis","15bis","15-bis","15 ter","15ter","15-ter","15 quater","15quater","15-quater","15 quinquies","15quinquies","15-quinquies","15 sexies","15sexies","15-sexies","15 septies","15septies","15-septies","15 octies","15octies","15-octies","15 novies","15novies","15-novies","15 decies","15decies","15-decies","16 bis","16bis","16-bis","16 ter","16ter","16-ter","16 quater","16quater","16-quater","16 quinquies","16quinquies","16-quinquies","16 sexies","16sexies","16-sexies","16 septies","16septies","16-septies","16 octies","16octies","16-octies","16 novies","16novies","16-novies","16 decies","16decies","16-decies","17 bis","17bis","17-bis","17 ter","17ter","17-ter","17 quater","17quater","17-quater","17 quinquies","17quinquies","17-quinquies","17 sexies","17sexies","17-sexies","17 septies","17septies","17-septies","17 octies","17octies","17-octies","17 novies","17novies","17-novies","17 decies","17decies","17-decies","18 bis","18bis","18-bis","18 ter","18ter","18-ter","18 quater","18quater","18-quater","18 quinquies","18quinquies","18-quinquies","18 sexies","18sexies","18-sexies","18 septies","18septies","18-septies","18 octies","18octies","18-octies","18 novies","18novies","18-novies","18 decies","18decies","18-decies","19 bis","19bis","19-bis","19 ter","19ter","19-ter","19 quater","19quater","19-quater","19 quinquies","19quinquies","19-quinquies","19 sexies","19sexies","19-sexies","19 septies","19septies","19-septies","19 octies","19octies","19-octies","19 novies","19novies","19-novies","19 decies","19decies","19-decies","20 bis","20bis","20-bis","20 ter","20ter","20-ter","20 quater","20quater","20-quater","20 quinquies","20quinquies","20-quinquies","20 sexies","20sexies","20-sexies","20 septies","20septies","20-septies","20 octies","20octies","20-octies","20 novies","20novies","20-novies","20 decies","20decies","20-decies"],"word_bigrams":["accise armonizzate","ires irpeg","rapporti con","violazioni sanzioni","agevolazioni esenzioni","delle merci","accertamento controlli","con l'af","condono amnistia","amnistia concordato","ambito applicazione","soggetti passivi","giochi lotterie","riscossione versamento","tributi locali","locali vari","pubbliche affissioni","accise non","non armonizzate","imposta sulle","armonizzate prodotti","prodotti energetici","energetici elettricità","ipotecarie catastali","armonizzate alcole","base imponibile","successioni donazioni","dei beni","imposte ipotecarie","sulle concessioni","erariale trascrizione","pubblicità pubbliche","tasse automobilistiche","termini per","imposta erariale","imposta registro","sulle assicurazioni","applicazione presupposti","determinazione dell'imposta","sulle successioni","imposta sugli","sugli intrattenimenti","contratti borsa","dati notizie","imposte sulle","modalità termini","concessioni governative","della tassa","pubblico insegnamento","tassa sui","sui contratti","canone abbonamento","abbonamento radiodiffusioni","enti pubblici","imposta bollo","servizi estimativi","tasse sulle","scritture contabili","prodotti agricoli","dichiarazione dei","finanza pubblica","politica monetaria","tasse sul","sul pubblico","dei redditi","codice fiscale","rapporto lavoro","pubblicità immobiliare","determinazione della","agenzie fiscali","enti non","diritti tributi","tributi indiretti","indiretti vari","impresa mercato","del servizio","non residenti","dello stato","richiesta dati","della dichiarazione","regime speciale","territorio doganale","del ricorso","dei comuni","politica sociale","violazioni relative","gestione del","delle dichiarazioni","determinazione del","dei prodotti","vari imposta","disposizioni generali","dei prezzi","irpef redditi","catasto terreni","degli uffici","del personale","operazioni straordinarie","dei diritti","conto corrente","del canone","lavoro tempo","degli atti","della riscossione","degli enti","misure cautelari","contabili d'impresa","estimi catastali","catastali classamento","non commerciali","beni immobili","diritti reali","tassa sulle","catasto urbano","del provvedimento","determinazione delle","delle sanzioni","contenzioso imposta","cessione beni","del patrimonio","tutela della","per gli","condono imposta","normativa doganale","relative alla","società persone","delle regioni","dei termini","del processo","persone fisiche","del codice","d'impresa contabilità","ricorsi contro","lavoro autonomo","delle imposte","anagrafe tributaria","debito pubblico","vari tassa","tributi speciali","mutua assistenza","liquidazione coatta","esenzioni imposta","spese per","dei servizi","per contribuenti","nazionali internazionali","valutazioni per","consulenze tecniche","tecniche fini","fini non","non fiscali","accertamento liquidazione","registro delle","registrazione delle","regimi doganali","redditi prodotti","perfezionamento passivo","provvedimento amministrativo","redditi lavoro","lavoro dipendente","procedura normale","occupazione aree","aree pubbliche","redditi società","programmazione economica","momento impositivo","sanzioni amministrative","principi generali","risorse proprie","direzioni centrali","determinazione misura","periodo d'imposta","servizi informatici","modalità per","addizionale regionale","degli immobili","presupposto dell'imposta","del contribuente","per presentazione","congruità collaudi","paesi terzi","arti professioni","agevolazioni imposta","del consumatore","doppia imposizione","denuncia variazioni","uffici locali","del procedimento","atti accertamento","diritti doganali","assistenza fiscale","irap ilor","scambio informazioni","consulenza giuridica","pubblicità con","accordi convenzioni","finanze comunitarie","enti locali","cassa previdenza","traffici illeciti"]}
;
    
    // Combina tutte le query
    const ALL_QUERIES = [
        ...ANALYSIS_DATA.single_chars,
        ...ANALYSIS_DATA.bigrams,
        ...ANALYSIS_DATA.trigrams,
        ...ANALYSIS_DATA.words,
        ...ANALYSIS_DATA.prefixes,
        ...ANALYSIS_DATA.sigle,
        ...ANALYSIS_DATA.years,
        ...ANALYSIS_DATA.articles,
        ...ANALYSIS_DATA.num_letter_combinations,
        ...ANALYSIS_DATA.word_bigrams
    ];
    
    console.log(`\n📊 QUERY DA ESEGUIRE:`);
    console.log(`  - Caratteri singoli:      ${ANALYSIS_DATA.single_chars.length}`);
    console.log(`  - Bigrammi:               ${ANALYSIS_DATA.bigrams.length}`);
    console.log(`  - Trigrammi:              ${ANALYSIS_DATA.trigrams.length}`);
    console.log(`  - Parole:                 ${ANALYSIS_DATA.words.length}`);
    console.log(`  - Prefissi:               ${ANALYSIS_DATA.prefixes.length}`);
    console.log(`  - Sigle:                  ${ANALYSIS_DATA.sigle.length}`);
    console.log(`  - Anni:                   ${ANALYSIS_DATA.years.length}`);
    console.log(`  - Articoli:               ${ANALYSIS_DATA.articles.length}`);
    console.log(`  - Combinazioni num+lett:  ${ANALYSIS_DATA.num_letter_combinations.length}`);
    console.log(`  - Bigrammi parole:        ${ANALYSIS_DATA.word_bigrams.length}`);
    console.log(`\n  🎯 TOTALE: ${ALL_QUERIES.length} query`);
    console.log(`  ⏱️  Tempo stimato: ~${Math.ceil(ALL_QUERIES.length * DELAY / 60000)} minuti\n`);
    
    // ========================================================================
    // FUNZIONI
    // ========================================================================
    
    async function fetchSolrSuggestions(searchTerm) {
        const url = BASE_URL + SOLR_ENDPOINT;
        const solrQuery = `{!boost b=score}kind:"key" AND key:${searchTerm}*`;
        const params = new URLSearchParams({
            rows: '100',
            q: solrQuery,
            wt: 'json',
            indent: 'off',
            fl: 'key'
        });
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: params.toString()
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.response && data.response.docs) {
                    const suggestions = data.response.docs
                        .map(doc => doc.key ? doc.key[0] : null)
                        .filter(k => k !== null);
                    return {
                        suggestions: suggestions,
                        total: data.response.numFound
                    };
                }
            }
            return { suggestions: [], total: 0 };
        } catch (error) {
            console.error(`❌ Errore per "${searchTerm}":`, error.message);
            return { suggestions: [], total: 0 };
        }
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    function downloadText(text, filename) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // ========================================================================
    // ESTRAZIONE PRINCIPALE
    // ========================================================================
    
    console.log('🚀 INIZIO ESTRAZIONE...\n');
    
    const allSuggestions = new Set();
    const suggestionsByQuery = {};
    const stats = {
        totalQueries: 0,
        successfulQueries: 0,
        failedQueries: 0,
        totalSuggestionsFound: 0,
        startTime: Date.now()
    };
    
    let progressCounter = 0;
    const progressInterval = Math.max(1, Math.floor(ALL_QUERIES.length / 50));
    
    for (const query of ALL_QUERIES) {
        stats.totalQueries++;
        progressCounter++;
        
        const result = await fetchSolrSuggestions(query);
        
        if (result.suggestions.length > 0) {
            stats.successfulQueries++;
            stats.totalSuggestionsFound += result.suggestions.length;
            suggestionsByQuery[query] = result.suggestions;
            
            result.suggestions.forEach(s => allSuggestions.add(s));
        } else {
            stats.failedQueries++;
        }
        
        // Progress update
        if (progressCounter % progressInterval === 0 || progressCounter === ALL_QUERIES.length) {
            const progress = Math.floor((progressCounter / ALL_QUERIES.length) * 100);
            const elapsed = Math.floor((Date.now() - stats.startTime) / 1000);
            const eta = Math.floor((elapsed / progressCounter) * (ALL_QUERIES.length - progressCounter));
            
            console.log(`📊 Progresso: ${progress}% (${progressCounter}/${ALL_QUERIES.length}) | ` +
                       `Unici: ${allSuggestions.size} | ` +
                       `Elapsed: ${elapsed}s | ETA: ${eta}s`);
        }
        
        await sleep(DELAY);
    }
    
    // ========================================================================
    // RISULTATI FINALI
    // ========================================================================
    
    const finalSuggestions = Array.from(allSuggestions).sort();
    const elapsedMinutes = Math.floor((Date.now() - stats.startTime) / 60000);
    
    console.log('\n' + '='.repeat(70));
    console.log('✅ ESTRAZIONE COMPLETATA!');
    console.log('='.repeat(70));
    console.log(`\n📊 STATISTICHE:`);
    console.log(`  Query eseguite:           ${stats.totalQueries}`);
    console.log(`  Query con risultati:      ${stats.successfulQueries}`);
    console.log(`  Query senza risultati:    ${stats.failedQueries}`);
    console.log(`  Suggerimenti totali:      ${stats.totalSuggestionsFound}`);
    console.log(`  Suggerimenti UNICI:       ${finalSuggestions.length}`);
    console.log(`  Tempo impiegato:          ${elapsedMinutes} minuti`);
    
    // Prepara dati finali
    const finalData = {
        metadata: {
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleString('it-IT'),
            url: window.location.href,
            source: 'Solr autocomplete - Cassazione (Analisi Esaustiva)',
            extraction_stats: {
                total_queries: stats.totalQueries,
                successful_queries: stats.successfulQueries,
                failed_queries: stats.failedQueries,
                total_suggestions_found: stats.totalSuggestionsFound,
                unique_suggestions: finalSuggestions.length,
                elapsed_time_minutes: elapsedMinutes
            }
        },
        suggestions: finalSuggestions
    };
    
    const detailedData = {
        metadata: finalData.metadata,
        suggestions_by_query: suggestionsByQuery,
        query_categories: {
            single_chars: ANALYSIS_DATA.single_chars,
            bigrams: ANALYSIS_DATA.bigrams,
            trigrams: ANALYSIS_DATA.trigrams,
            words: ANALYSIS_DATA.words,
            prefixes: ANALYSIS_DATA.prefixes,
            sigle: ANALYSIS_DATA.sigle,
            years: ANALYSIS_DATA.years,
            articles: ANALYSIS_DATA.articles,
            num_letter_combinations: ANALYSIS_DATA.num_letter_combinations,
            word_bigrams: ANALYSIS_DATA.word_bigrams
        }
    };
    
    // Scarica i file
    console.log('\n📥 Scaricamento file...\n');
    downloadJSON(finalData, 'cassazione_exhaustive.json');
    downloadJSON(detailedData, 'cassazione_exhaustive_detailed.json');
    downloadText(finalSuggestions.join('\n'), 'cassazione_keywords_exhaustive.txt');
    
    // Top suggerimenti
    console.log('📋 Primi 30 suggerimenti estratti:');
    finalSuggestions.slice(0, 30).forEach((s, i) => {
        console.log(`  ${(i + 1).toString().padStart(2, '0')}. ${s}`);
    });
    
    if (finalSuggestions.length > 30) {
        console.log(`  ... e altri ${finalSuggestions.length - 30} suggerimenti`);
    }
    
    console.log('\n✅ File scaricati:');
    console.log('   - cassazione_exhaustive.json');
    console.log('   - cassazione_exhaustive_detailed.json');
    console.log('   - cassazione_keywords_exhaustive.txt');
    
    console.log('\n💡 Dati disponibili in: window.cassazioneExhaustive');
    console.log('='.repeat(70) + '\n');
    
    // Salva in window
    window.cassazioneExhaustive = finalData;
    window.cassazioneExhaustiveDetailed = detailedData;
    
    return finalData;
    
})().catch(error => {
    console.error('❌ ERRORE FATALE:', error);
    console.error('Stack:', error.stack);
});
