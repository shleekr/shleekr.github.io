---
layout: post
title: 바이그램 한국어 품사 태거
---

<div class="message">
<bold> <font color="black"> Abstract </font> </bold> 
This blog is a study on making a bigram Korean part-of-speech tagger. 
I implemented a Korean morphological transducer (please read the former blog I wrote),
and composed it with a bigram transducer, which is very common in 
statistical natural language processing society.
I tried to making a single transducer 
(not to need to compose the transducers on-the-fly when an input text is given.),
The resulting transducer is so big, about 600Mbyte-sized,
while I think there would be another more effective way of making the compact transducer.
</div>

이 블로그에서는 바이그램 한국어 형태소 분석기를 오픈하고자 합니다.
어떻게 만들었는지 짧게 설명하고 최종 파일을 올립니다.

### 어떻게 만들었나? 

우선, 바이그램 품사 태거는 아래의 수식과 같다.

<center>
![bigram 품사 태거](public/images/bigram_eq.jpg) 
</center>

위 수식을 수행하는 하나의 확률 유한 상태 변환기 (weighted finite state transducer)를
만들기 위해서 세 개의 변환기를 준비하였다.

* 한국어 형태소 분석 변환기 (M).  
  이전 블로그에서 설명하였듯이, [foma](http://foma.googlecode.com)를 이용해서 
  한국어 유한 상태 변환기를 만들면, 그 변환기는, upper language (입력)가 형태소, 
  lower language (출력)는 표층형인 변환기이다.
  이를 invert (입출력을 뒤집는)한 후 AT&T format으로 출력한 후 이를 
  [openfst](http://www.openfst.org)의 이진 파일 형태로 바꾼다.
* 품사에서 어휘가 발생할 확률 <em> P(w<sub>i</sub> | t<sub>i</sub>) </em>을 부여한
  변환기 (L). 이는 앞 블로그에서 unigram 변환기와 같은 형식이나 확률만 조건부 확률을 부여한다.
  아래 그림과 같은 변환기이다.

<center>
![lexical 확률 변환기](public/images/lexprob.jpg) 
</center>

* 이전 품사에서 그 다음 품사로 천이할 확률을 가지고 있는 변환기 (T).
  이 변환기는 품사 천이 확률 <em> P(t<sub>i</sub> | t<sub>i-1</sub>) </em>을 표현하기 위해
   사용된 변환기이다. 변환기에 있는 ρ (rho) 심벌은 '어떠한 심벌과도 매칭'되는 심벌로서,
   입력과 출력이 모두 ρ이므로 어떠한 입력이든 그대로 출력된다는 것을 의미한다.
   아래 그림은 세 개의 품사 nc, np, pt만 존재한다고 가정할 때의 변환기 모양이다.
   ('INI'는 initial state를 의미하는 것으로, 문장의 첫 번째 단어가 시작될 때의 품사 천이
	정보를 표현하기 위해 사용된 state이다.)

<center>
![bigram 변환기](public/images/bigramfst.jpg) 
</center>

위에서 구한 세 개의 변환기 M, L, T를 모두 composition하면 하나의 변환기가 나오게 되며,
이것이 최종적으로 우리가 구하고자 하는 변환기이다.
참고로 ρ 심벌을 이용하여 composition을 하기 위해서는 [openfst](http://www.openfst.org)에 있는
fstcompose를 사용하는 것이 아니라 다른 composition 프로그램을 사용해야 된다.
이를 위해 [fstphirhocompose](https://github.com/dogancan/lexicon-unk)를 사용하였다.

### 실행하기

최종 만들어진 파일의 크기를 압축하여도 크기가 커서, 
두 개의 파일 [bitagger_aa](public/data/bitagger_aa)와 
[bitagger_ab](public/data/bitagger_ab)로 나누었다.
이 파일은 unix 명령어 split을 이용해서 단순히 나눈 것이어서,
아래와 같이 실행하면 원래의 하나의 파일로 만들 수 있다.

<pre>
shlee@shlee:~$ <em><font color="red">ls -l</font></em>
-rw-r--r-- 1 shlee shlee  94371840 10월  4 bitagger_aa
-rw-r--r-- 1 shlee shlee  89417271 10월  4 bitagger_ab
shlee@shlee:~$ <em><font color="red">cat bitagger_* > bitaggerfile.tar.gz</font></em>
shlee@shlee:~$ <em><font color="red">ls -l</font></em>
-rw-r--r-- 1 shlee shlee  94371840 10월  4 bitagger_aa
-rw-r--r-- 1 shlee shlee  89417271 10월  4 bitagger_ab
-rw-r--r-- 1 shlee shlee 183789111 10월  4 bitaggerfile.tar.gz
shlee@shlee:~$ <em><font color="red">tar zxvf bitaggerfile.tar.gz</font></em> 
BiTagger/
BiTagger/testme.txt
BiTagger/korinvertwordbifinal.fst
BiTagger/korinvert.sym
BiTagger/kyfd
BiTagger/koreanbi.xml
BiTagger/wordbiprob.sym
shlee@shlee:~$ cd BiTagger/
shlee@shlee:~/BiTagger$ <em><font color="red">cat testme.txt | ./kyfd koreanbi.xml</font></em>
--------------------------
-- Started Kyfd Decoder --
--------------------------
...
</pre>

이 블로그에서 올린 바이그램 태거의 성능은 교과서에 나오는 바이그램 태거와 비슷하거나 못 할 것으로 생각됩니다. 
제가 unigram backoff 모델을 적용하지 않았고, 또한 프로그램의 결과를 보면서 튜닝하지 않았기 때문입니다. 
하지만 한국어 처리를 공부하고 계신 분은 위 태거를 이용해서 가장 기본이 되는 태거의 성능은 어떤가를 알고 싶을 때
도움이 될 것 같습니다.

### 컴파일 관련

신명철님께서 [Rouzeta 컴파일](https://github.com/dsindex/rouzeta) 글과,
[Rouzeta 파이썬 랩퍼](https://github.com/dsindex/ckyfd) 글을 올리셨습니다. 참고하세요.

