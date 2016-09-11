---
layout: post
title: 유한 상태 기반의 한국어 형태소 분석기
---
   본 연구는 유한 상태 변환기 (finite state transducer) 기반의 한국어 형태소 
분석기에 대한 연구이다. 이 연구의 최종 목표는 한국어 문장에서 나타날 수 있는 모든 심벌들의 
열을 입력으로 받은 후 다른 종류의 정보처리 방법을 통하지 않고 오로지 상태 변환기를 통해서만
형태소 분석 및 품사 태깅까지를 한번에 완료시키는 것이다.
이를 위해서, 본 연구에서는 한국어 형태소 분석을 위한 여러가지 규칙들을 직접 기술하여
한국어 형태소 분석 상태 변환기를 만들고, 이 변환기에 품사태깅에 필요한 확률을 부여하는
방식으로 변환기를 구성하였다. 

### 서론

형태소 분석이란 문장이 주어졌을 때 의미를 가지는 작은 단위로 문장을 나누는 일을 말한다.
예를 들어, 

<div class="message">
  당신이 고마워졌다.
</div>
라는 문장이 있다면, 아래와 같이 분석되어진다.

<div class="message">
  당신/<sub>체언</sub> + 이/<sub>주격조사</sub> 고맙/<sub>ㅂ불규칙, 용언</sub>
  + 어/<sub>보조적연결어미</sub> + 지/<sub>보조용언</sub> + 었/<sub>선어말어미</sub>
  + 다/<sub>어말어미</sub>
</div>

이러한 형태소 분석 단계는 구문분석의 앞단에서 사용되거나,
검색 시스템에서 인덱싱을 위한 단어추출에 사용된다.
이 외에도 음성인식을 위한 기본 인식 단위를 결정하는데 사용될 수도 있고,
음성 합성에서 문장을 분석하기 위해서도 사용된다.

형태소 분석을 하는 방법들로 가장 흔하게 사용되는 방법은,
트라이 (trie)로 된 사전을 가지고 있는 상태에서
입력 어절에 대해서 좌에서 우, 혹은 우에서 좌로 트라이를 찾아가면서 가능한 모든 형태소들을 찾고,
이들을 격자 (lattice)로 표현시켜서 네트워크를 구성하는 방식이다.

!['나는'의 형태소 분석 과정](public/images/nanun.jpg) 

이 방법을 기초로 하면서 불규칙 용언들에 대해서 원형만을 사전에 가지고 
형태소를 분석하거나<a href='#1'>[1]</a> 혹은 이형태까지를 미리 사전에 등록하는 두 가지 방식이
주로 사용된다<a href='#2'>[2]</a>.
한국어 형태소 분석은 언어처리에서 기초적인 단계이고 유틸리티로서의 역할이
높기때문에 속도가 매우 중요한데 이를 위해서 음절 정보를 이용한다거나<a href='#3'>[3]</a>,
부분 어절에 대한 기분석 사전을 이용하는 등 다양한 아이디어들이 존재한다<a href='#4'>[4]</a>.

본 사이트에서는 Finite State Transducer를 이용하여 만든 한국어 형태소 분석기 Rouzeta를 소개한다.
Rouzeta는 한국어의 모든 규칙/불규칙 현상을 처리할 수 있으며, 분석기를
[foma](http://foma.googlecode.com)와 [xerox finite state tools](http://web.stanford.edu/~laurik/fsmbook/home.html)에서
모두 테스팅해 보았다.

### 유한 상태 형태론 (Finite State Morphology) 

유한 상태 형태론에 대해서는 [K. R. Beesley](https://www.linkedin.com/in/krbeesley)와
[L. Karttunen](http://web.stanford.edu/~laurik)이 저술한 
[Finite State Morphology](https://www.amazon.com/Finite-State-Morphology-Kenneth-Beesley/dp/1575864347)를
읽어보기 바란다. 이 장에서는 간략하게 설명하겠다.
우리가 흔히 알고 있는 유한 상태 머신 (Finite State Machine)은 입력 심벌, 그리고 노드에서 다른 노드로 
이동할 때 해당 입력 심벌을 소비하면서 이동하는 엣지로 구성되어 있으며,
모든 심벌들이 소비되었을 때 특정 상태에 도달하게 되고 그 상태 (노드)가 단말 노드일 경우
미리 부여된 노드의 의미로 심벌 스트링을 해석한다.
한편, 유한 상태 변환기 [Finite State Transducer](https://en.wikipedia.org/wiki/Finite-state_transducer)는
입력 심벌 뿐만 아니라 출력 심벌도 정의가 되고, 노드에서 노드로 점프할 때 입력 심벌을 소비하면서
동시에 출력 심벌이 출력되는 것이다.

여기에서 중요한 점은, 이렇게 임의의 시스템 입력이 특정 심벌들 열(sequence)이며
프로세싱을 거친 후에 특정 심벌들 열(sequence)로 나오는 경우에 해당하는 프로그램들이 많다는 것이다.
예를 들어, 영어 문장을 입력으로 받아 한국어 문장을 출력하는 기계번역기 (Machine Translation)라든가,
문장을 입력으로 받아 자동으로 그 문장을 교정하는 문장 교정기 (Automatic Speller)라든가,
심지어 발음 열을 입력으로 받아서 문장을 출력하는 것도 음성 인식기 개발에서 사용될 수 있다.

아래 이미지를 보면, 입력이 [Rosetta](https://en.wikipedia.org/wiki/Rosetta_Stone)이고
출력이 발음 표기인 Rouzeta인 finite state transducer이다.

![Rosetta:Rouzeta finite state transducer 예](public/images/rouzeta.jpg) 

위 그림에서 입력과 출력이 동일할 경우는 심벌이 하나만 적혀 있다 (R, o, e, t, a의 경우).
한편 <0:u>는 입력이 없을 때 u를 출력한다는 의미이고, < t:0>는 입력이 t인데 출력을 하지 않는다는 뜻이다.
(그림에서 0은 오토마타 이론에서 epsilon을 의미하는 것으로 no-symbol이다)
위와 같이 함으로써 Rosetta를 입력으로 넣으면, Rouzeta가 출력되게 된다.

그렇다면, 이러한 유한 상태 변환기가 어떻게 형태소 분석기와 관계가 있다는 뜻인가?
형태소 분석이란 말은 말 그대로 '분석'을 의미하는데, 이것을 분석 심벌들 출력이라고 보고,
'고마워'라는 표층형과 이를 이루는 어휘형 '고맙 [ㅂ 불규칙] [용언]', '어 [어미]'간의 
관계를 유한 상태 변환기로 표현한다는 것이다. 즉, Trie와 같은 자료구조를 이용하면서
프로그램 내부에서 loop를 이용하여 후보를 사전에서 찾아보면서 분석 결과를 관리하는
기존의 모델과 비교할 때, 이 방법은 어휘형과 표층형을 입력/출력 스트링의 관계로 보고
각 스트링간의 관계를 기술하고 이를 컴파일 (compile)하여 거대한 유한 상태 변환기를 
만들면 이것이 곧 형태소 분석기가 된다.
이 방법이 기존 방법과 가장 큰 차이는 무엇인가? 바로 언어의 해석을 descriptive하게 
기술한다는 것이다. 사전을 찾아보면서 내부적으로 어절의 구조를 그리는 방식은
프로그램의 형식이 절차적 (procedual)일 수 밖에 없다. 하지만 유한 상태 변환기는
(물론 내부적으로 상태 (state)를 따라가면서 loop가 필요하기는 하지만)
언어의 해석을 처리함에 있어서 언어 현상을 descriptive한 언어로 표현하기 때문에
좀 더 언어 현상 본질에 더 가깝게 다가가 해석할 수 있다.

또한 유한 상태 변환기의 장점 중 하나는 입력/출력을 서로 바꾸는 것이 매우 쉽기 때문에
만약 형태소 분석기를 만들고, 이 변환기의 입출력을 서로 바꾸면 어절 생성기 
(형태소를 나열했을 때 표층형을 만드는 생성기)를 만들 수 있다.

입력이 '고맙 [ㅂ 불규칙] [용언] 어 [어미]'이고 출력이 '고마워'인 
유한 상태 변환기는 아래와 같다. 입력과 출력을 바꾸면 형태소 분석기가 되고,
아래 변환기는 어절 생성기라고 볼 수 있다. 
(통상적으로 유한 상태 형태론에서는 입력이 어휘형이고 출력이 표층형이다.)

![고마워 finite state transducer 예](public/images/komawe.jpg) 

### 한국어 유한 상태 형태론 (Korean Finite State Morphology) 

그렇다면, 이제 궁금증이 생길 것이다.
유한 상태라는 의미는 말 그대로 유한한 심벌 (본 실험에서는 utf-8로 코딩된 음절 하나)들로 
이루어진 스트링에 대해서 하나의 심벌씩 소비하면서 존재할 수 있는 상태 (state) 수가 유한하다는 것인데, 
형태소들간의 접점에서 일어나는 현상들이 모두 유한한 상태 수로 표현 가능할 것인가?
또한 통상적으로 형태소들의 접점에서 발생하는 현상들은 그 접점의 오른쪽 스트링을
일정 개수 이상 보아야 그 접점에서 발생하는 현상을 제대로 표현하는 경우가 있는데
어떻게 이러한 (procedual하게 보이는) 현상이 descriptive하게 표현될 수 있다는 것인가?
이에 대해서 좀 더 알아보고 싶은 분은 Kaplan과 Kay가 쓴 논문<a href='#5'>[5]</a>를 읽어보기 바란다.

예를 들어, A 라는 심벌열이 왼쪽에 C 문맥, 오른쪽에 D 문맥이 있을 때 B 심벌열로 바뀌는 것을 
아래와 같이 기술할 수 있다. 

> A -> B / C _ D

이를 유한 상태 변환기로 표현할 수 있는데, 다음은 [foma](http://foma.googlecode.com)로 컴파일해 본 결과이다. 

<pre>
shlee@shlee:~$ foma
Foma, version 0.9.18alpha (svn r0)
Copyright © 2008-2015 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"

Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.

foma[0]: <em><font color="red">define A a -> b || c _ d ;</font></em>
defined A: 634 bytes. 4 states, 16 arcs, Cyclic.
foma[0]: <em><font color="red">regex A ;</font></em>
634 bytes. 4 states, 16 arcs, Cyclic.
foma[1]: <em><font color="red">view</font></em>
</pre>


![a -> b || c _ d](public/images/a_bcd.jpg) 

위 그림에서 @ 심벌은 결과 유한 상태 변환기 이외에 있는 모든 심벌을 의미한다. 즉 정의되지 않은 심벌들이다.
변환기의 0번 상태에서 c a d를 입력한다고 가정해 보자. 그 결과 0 -> 1 -> 3 -> 0 상태 순으로
천이하면서 c b d가 출력된다는 것을 알 수 있다. 이렇게 좌우 문맥하에서의 심벌 변화를 
유한 상태 변환기로 표현할 수 있음을 알 수 있다.

그렇다면, 한국어 형태소 분석기를 위한 규칙 중 하나를 기술해 보자.
'ㄷ' 불규칙은 어간의 'ㄷ' 받침이 모음으로 시작하는 어미 앞에서 'ㄹ' 받침으로 바뀌는 활용으로
동사에만 있고 형용사에는 없다. 예를 들어, '깨닫 [ㄷ 불규칙] [용언] 아 [어미]'는
'깨달아'로 바뀌게 된지만 '믿 [용언] 어 [어미]'는 '믿어'로 바뀌는 규칙 활용을 한다.
만약, 하나의 음절을 초성, 중성, 종성으로 모두 나누어 처리하게 만들 수 있다면,
종성 'ㄷ'이 오른쪽에 '[ㄷ 불규칙] [용언] [초성 ㅇ]'으로 시작할 때 'ㄹ'로 바뀌게 만들면
될 것이다. 이를 간단하게 테스팅해 보면 다음과 같다.

<pre>
foma[0]: <em><font color="red">define A %_ㄷ -> %_ㄹ || _ %/irrd %/vb ㅇ ;</font></em>
defined A: 898 bytes. 7 states, 30 arcs, Cyclic.
foma[0]: <em><font color="red">regex A ;</font></em>
898 bytes. 7 states, 30 arcs, Cyclic.
foma[1]: <em><font color="red">view</font></em>
</pre>

![ㄷ 불규칙 현상의 규칙](public/images/d_irr.jpg) 

위에서 '/irrd'는 '[ㄷ 불규칙]'을 의미하는 심벌이고, '/vb'는 '[용언]'을 의미하는 심벌이다.

### Composition

한국어 형태소 분석을 위한 여러 현상들, 'ㅂ' 불규칙, 'ㄷ' 불규칙, 그리고 모음 조화 현상 등
각종 현상들이 어떻게 하나의 유한 상태 변환기로 표현될 수 있을까?
또한 우리는 입력을 utf-8 한글 음절을 기본 단위로 한다고 했는데, 각종 음운 현상들은
모두 자소 수준에서 이루어져야 한다. 입력은 음절 심벌들이고, 음운 처리는 자소 심벌들이,
그리고 다시 결과를 표현할 때는 음절 심벌들로 표현되기 위해 어떻게 해야 하는가?
이 모든 것들이 유한 상태 변환기의 특징인 composition operator를 이용해서 처리할 수 있다.

두 개의 유한 상태 변환기 A, B를 정의하자. 그리고 A .o. B ( A composition B)를 수행한다.
이 operator는 A의 출력이 B의 입력이 되어 A의 입력, B의 출력으로 이루어진 새로운 
유한 상태 변환기 C를 만들게 된다.
예를 들어, '하나'라는 한국어 단어를 'one'이라는 영어 단어로 바꾸는 변환기를 A라고 하고,
'one'이라는 영어 단어를 'いち'라는 일본어 단어로 바꾸는 변환기를 B,
'いち'라는 일본어 단어를 한자 '一'로 바꾸는 변환기를 C라고 할 때,
세 개의 변환기를 composition한 결과는 입력이 '하나'이고 출력이 '一'인 변환기가 만들어진다.

<pre>
shlee@shlee:~$ foma
Foma, version 0.9.18alpha (svn r0)
Copyright © 2008-2015 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"

Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.

foma[0]: <em><font color="red">define A [하나:one] ;</font></em>
defined A: 235 bytes. 2 states, 1 arc, 1 path.
foma[0]: <em><font color="red">define B [one:いち] ;</font></em>
defined B: 235 bytes. 2 states, 1 arc, 1 path.
foma[0]: <em><font color="red">define C [いち:一] ;</font></em>
defined C: 235 bytes. 2 states, 1 arc, 1 path.
foma[1]: <em><font color="red">regex A .o. B .o. C ;</font></em>
294 bytes. 2 states, 1 arc, 1 path.
foma[1]: <em><font color="red">view</font></em>
</pre>

![composition](public/images/one.jpg) 

위와 같은 방법을 이용해서, 하나의 음절을 자소 단위로 나누고, 자소 수준에서의 각종
규칙들을 처리한 후, 다시 자소 단위를 음절로 합치면, 
내부적으로는 자소 단위로 규칙들이 적용되지만, 결과적으로 만들어지는 최종 변환기는
자소 심벌이 없는 변환기가 만들어진다.

통상적으로 형태소 분석기는 '분석'이라는 말 그대로 입력이 표층형, 출력이 어휘형으로
나오게 만드는데 반면, 유한 상태 변환기로 분석기를 만들 때는 입력이 어휘형, 
출력이 표층형이 되게 규칙을 기술한 후, 최종 변환기를 inverse시켜서 형태소 분석을 수행한다.

구현된 형태소 분석기에서 각종 규칙을 composition하여 ARules (Alternation Rules)로 정의하는 코드 부분은
아래와 같다. (실제 코드에서는 좀 더 긴 이름으로 정의되어 있는데
화면에 잘 보이게 하기 위해서 변환기 이름을 줄였습니다.)

<pre>
define ARules NPFilter    .o. ! 체언 + 조사 규칙 적용 : 사과는/사람은
              VEFilter    .o. ! 용언 + 어미 불가 필터 : 아름답+는/고마웠+아야지
              VHarmony    .o. ! 용언 모음 조화        : 막아/저어
              RuleYI      .o. ! '이' 축약 & '이' 생략 : 사과다/사과였다/가졌다
              DropEU      .o. ! '으' 탈락 현상        : 써도
              InsertEU    .o. ! '으' 삽입 현상        : 먹으면
              IrrConjO    .o. ! '오' 불규칙 현상      : 다오
              DropL       .o. ! 'ㄹ' 탈락 현상        : 아니까
              DropS       .o. ! 'ㅅ' 불규칙 현상      : 그어
              ConjEAE     .o. ! 'ㅐ'/'ㅔ'의 '어'탈락  : 메, 개, 갰다
              IrrConjD    .o. ! 'ㄷ' 불규칙 현상      : 깨달아
              IrrConjB    .o. ! 'ㅂ' 불규칙 현상      : 고와
              IrrConjl    .o. ! '르' 불규칙 현상      : 굴러
              IrrConjL    .o. ! '러' 불규칙 현상      : 푸르러
              IrrConju    .o. ! '우' 불규칙 현상      : 퍼
              IrrConjYEO  .o. ! '여' 불규칙 현상      : 하여, 해
              IrrEola     .o. ! '거라'/'너라' 불규칙  : 자거라, 오너라
              IrrConjH    .o. ! 'ㅎ' 불규칙 현상      : 하얘, 빨간
              ConjDiph    .o. ! 용언+어미 모음 축약   : 가(가+아), 됐다 (되+었+다)
             ReducedWords .o. ! 줄임말들 처리         : 흔치 않다.
              FilterOut   .o. ! 기본적인 는/을/는다의 과분석 제거
              ChangeNullCoda ;! Null 종성 삽입/삭제
</pre>

### 코퍼스 및 품사 정의

유한 상태 형태소 분석기 (Rouzeta)는 [세종 코퍼스](http://ithub.korean.go.kr/user/guide/corpus/guide1.do)를
처리하여 만들었다. 한편, 세종 코퍼스에서 사용하고 있는 품사가 덜 세분되어있는 경향이 있어서,
본 연구에서는 본인이 계속 사용해 오던 품사 셋으로 코퍼스를 수정하였다.
태깅되어 있는 코퍼스를 변환하는 것이 쉽지 않았는데, 특히나 세종 코퍼스에 오류가 너무 많았으며,
이를 패턴별로 프로그램을 작성하여 자동으로 수정도 하였고, 오류가 몇 개 되지 않았을 때에는 직접 수정하였다. 
수정된 코퍼스를 오픈할 수 있는지, 현 시점에서 최초 세종 코퍼스의 라이센스를 검색해 보았으나 찾을 수 없어서
현 시점에서는 수정된 코퍼스를 올리지 않겠다.

구현된 형태소 분석기에서 사용한 품사 리스트는 아래와 같다.
품사 심벌을 알파벳 두 글자로 표현하고, 첫번째 알파벳은 대분류 의미이고, 두번째 알파벳은 소분류 의미이다.
(여기서 사용된 품사 정의는 KAIST [김재훈](https://sites.google.com/site/nlpatkmu/home) 선배님이
 정리하셨던 것을 수정하여 사용합니다.)

<table>
  <thead>
    <tr>
      <th>품사</th>
      <th>심벌</th>
      <th>뜻</th>
      <th>예</th>
    </tr>
  </thead>
  <tbody>
    <tr>
     <td>접속부사</td>
     <td>ac</td>
     <td>conjunctive adverb</td>
     <td>또는, 그러나, ...</td>
    </tr>
    <tr>
     <td>부사</td>
     <td>ad</td>
     <td>adverb</td>
     <td>매우, 과연, ...</td>
    </tr>
    <tr>
     <td>의문부사</td>
     <td>ai</td>
     <td>interrogative adverb</td>
     <td>어디, 언제, ...</td>
    </tr>
    <tr>
     <td>지시부사</td>
     <td>am</td>
     <td>demonstrative adverb</td>
     <td>여기, 저기, ...</td>
    </tr>

    <tr>
     <td>의문관형사</td>
     <td>di</td>
     <td>interrogative adnoun</td>
     <td>어느, 몇, ...</td>
    </tr>
    <tr>
     <td>지시관형사</td>
     <td>dm</td>
     <td>demonstrative adnoun</td>
     <td>이, 그, 저, ...</td>
    </tr>
    <tr>
     <td>관형사</td>
     <td>dn</td>
     <td>adnoun</td>
     <td>새, 헌, ...</td>
    </tr>
    <tr>
     <td>수관형사</td>
     <td>du</td>
     <td>numeral adnoun</td>
     <td>한, 두, ...</td>
    </tr>

    <tr>
     <td>연결어미</td>
     <td>ec</td>
     <td>conjunctive ending</td>
     <td>~며, ~고, ...</td>
    </tr>
    <tr>
     <td>관형사형전성어미</td>
     <td>ed</td>
     <td>adnominal ending</td>
     <td>~는, ~ㄹ, ...</td>
    </tr>
    <tr>
     <td>어말어미</td>
     <td>ef</td>
     <td>final ending</td>
     <td>~다, ~는다, ...</td>
    </tr>
    <tr>
     <td>명사형전성어미</td>
     <td>en</td>
     <td>nominal ending</td>
     <td>~ㅁ, ~기 (두 개뿐) </td>
    </tr>
    <tr>
     <td>선어말어미</td>
     <td>ep</td>
     <td>prefinal ending</td>
     <td>~았, ~겠, ...</td>
    </tr>
    <tr>
     <td>보조적연결어미</td>
     <td>ex</td>
     <td>auxiliary ending</td>
     <td>~아, ~고, ...</td>
    </tr>
    <tr>
     <td>감탄사</td>
     <td>it</td>
     <td>interjection</td>
     <td>앗, 거참, ...</td>
    </tr>
    <tr>
     <td>동작성보통명사</td>
     <td>na</td>
     <td>active common noun</td>
     <td>가맹, 가공, ...</td>
    </tr>
    <tr>
     <td>보통명사</td>
     <td>nc</td>
     <td>common noun</td>
     <td>가관, 가극, ...</td>
    </tr>
    <tr>
     <td>의존명사</td>
     <td>nd</td>
     <td>dependent noun</td>
     <td>겨를, 곳, ...</td>
    </tr>
    <tr>
     <td>의문대명사</td>
     <td>ni</td>
     <td>interrogative pronoun</td>
     <td>누구, 무엇, ...</td>
    </tr>
    <tr>
     <td>지시대명사</td>
     <td>nm</td>
     <td>demonstrative pronoun</td>
     <td>이, 이것, ...</td>
    </tr>
    <tr>
     <td>수사</td>
     <td>nn</td>
     <td>numeral</td>
     <td>공, 다섯, ...</td>
    </tr>
    <tr>
     <td>인칭대명사</td>
     <td>np</td>
     <td>personal pronoun</td>
     <td>나, 너, ...</td>
    </tr>
    <tr>
     <td>고유명사</td>
     <td>nr</td>
     <td>proper noun</td>
     <td>YWCA, 홍길동, ...</td>
    </tr>
    <tr>
     <td>상태성보통명사</td>
     <td>ns</td>
     <td>stative common noun</td>
     <td>간결, 간절, ...</td>
    </tr>
    <tr>
     <td>단위성의존명사</td>
     <td>nu</td>
     <td>unit dependent noun</td>
     <td>그루, 군데, ...</td>
    </tr>
    <tr>
     <td>숫자</td>
     <td>nb</td>
     <td>number</td>
     <td>1, 2, ...</td>
    </tr>

    <tr>
     <td>부사격조사</td>
     <td>pa</td>
     <td>number</td>
     <td>~에, ~에서, ...</td>
    </tr>
    <tr>
     <td>접속조사</td>
     <td>pc</td>
     <td>conjunctive particle</td>
     <td>~나, ~와, ...</td>
    </tr>
    <tr>
     <td>관형격조사</td>
     <td>pd</td>
     <td>adnominal particle</td>
     <td>~의 (한 개) </td>
    </tr>
    <tr>
     <td>목적격조사</td>
     <td>po</td>
     <td>adnominal particle</td>
     <td> ~을, ~를, ~ㄹ </td>
    </tr>
    <tr>
     <td>서술격조사</td>
     <td>pp</td>
     <td>predicative particle</td>
     <td>~이~ (한 개) </td>
    </tr>
    <tr>
     <td>주격조사</td>
     <td>ps</td>
     <td>subjective particle</td>
     <td>~이, ~가, ... </td>
    </tr>
    <tr>
     <td>주제격조사</td>
     <td>pt</td>
     <td>thematic particle</td>
     <td>~은, ~는, (두 개) </td>
    </tr>
    <tr>
     <td>호격조사</td>
     <td>pv</td>
     <td>vocative particle</td>
     <td>~야, ~여, ~아, ... </td>
    </tr>
    <tr>
     <td>보조사</td>
     <td>px</td>
     <td>auxiliary particle</td>
     <td>~ㄴ, ~만, ~치고, ... </td>
    </tr>
    <tr>
     <td>인용격조사</td>
     <td>pq</td>
     <td>quotative particle</td>
     <td>~고, ~라고, ~라, ... </td>
    </tr>
    <tr>
     <td>보격조사</td>
     <td>pm</td>
     <td>complementary particle</td>
     <td>~이, ~가 (두 개) </td>
    </tr>

    <tr>
     <td>동사</td>
     <td>vb</td>
     <td>verb</td>
     <td>감추~, 같~, ... </td>
    </tr>
    <tr>
     <td>의문형용사</td>
     <td>vi</td>
     <td>interrogative adjective</td>
     <td>어떠하~, 어떻~, ... </td>
    </tr>
    <tr>
     <td>형용사</td>
     <td>vj</td>
     <td>adjective</td>
     <td>가깝~, 괜찮~, ... </td>
    </tr>
    <tr>
     <td>보조용언</td>
     <td>vx</td>
     <td>auxiliary verb</td>
     <td>나~, 두~, ... </td>
    </tr>
    <tr>
     <td>부정지정사</td>
     <td>vn</td>
     <td>auxiliary verb</td>
     <td>아니~ (하나) </td>
    </tr>

    <tr>
     <td>부사파생접미사</td>
     <td>xa</td>
     <td>adverb derivational suffix</td>
     <td>~게, ~이, ... </td>
    </tr>
    <tr>
     <td>형용사파생접미사</td>
     <td>xj</td>
     <td>adjective derivational suffix</td>
     <td>같~, 높~, 답~, ... </td>
    </tr>
    <tr>
     <td>동사파생접미사</td>
     <td>xv</td>
     <td>verb derivational suffix</td>
     <td>~하, ~시키, ... </td>
    </tr>
    <tr>
     <td>명사접미사</td>
     <td>xn</td>
     <td>noun suffix</td>
     <td>~군, ~꾼, ... </td>
    </tr>

    <tr>
     <td>쉼표</td>
     <td>xn</td>
     <td>comma</td>
     <td>:, ,, ... </td>
    </tr>
    <tr>
     <td>줄임표</td>
     <td>se</td>
     <td>ellipsis</td>
     <td>…  </td>
    </tr>
    <tr>
     <td>마침표</td>
     <td>sf</td>
     <td>sentence period</td>
     <td>!, ., ? </td>
    </tr>
    <tr>
     <td>여는따옴표</td>
     <td>sl</td>
     <td>left parenthesis</td>
     <td>(, <, [, ... </td>
    </tr>
    <tr>
     <td>닫는따옴표</td>
     <td>sr</td>
     <td>right parenthesis</td>
     <td>), >, ], ... </td>
    </tr>
    <tr>
     <td>이음표</td>
     <td>sd</td>
     <td>dash</td>
     <td>-, ... </td>
    </tr>
    <tr>
     <td>단위</td>
     <td>su</td>
     <td>unit</td>
     <td>Kg, Km, bps, ... </td>
    </tr>
    <tr>
     <td>화폐단위</td>
     <td>sy</td>
     <td>currency</td>
     <td>$, ￦, ... </td>
    </tr>
    <tr>
     <td>기타기호</td>
     <td>so</td>
     <td>other symbols</td>
     <td>α, φ, ... </td>
    </tr>
    <tr>
     <td>한자</td>
     <td>nh</td>
     <td>chinese characters</td>
     <td>丁, 七, 万, ... </td>
    </tr>
    <tr>
     <td>영어</td>
     <td>ne</td>
     <td>english words</td>
     <td>computer, ... </td>
    </tr>
  </tbody>
</table>

### Rouzeta & Tagger

본 절에서는 한국어 형태소 분석기 [Rouzeta](public/data/rouzeta.tar.gz)를 설명한다. 
Rouzeta는 두개의 폴더로 되어 있으며, Rouzeta 폴더에서는 형태소 분석을 위한 사전 및
어휘 조합 규칙들이 있으며, Tagger 폴더에는 unigram 확률 모델 방식의
한국어 품사 태거 (Korean part-of-speech tagger) WFST (weighted finite state transducer)가 들어 있다.
한국어 품사 태거를 만드는 방식은 우선, Rouzeta FST를 inverse 시킨 후 
(즉, 표층형이 입력이고 어휘형이 출력인 상태로 입출력을 바꿈),
이 FST를 [openfst](http://www.openfst.org) 형식으로 바꾸고, 
해당 FST에 미리 구해진 형태소 발생 확률을 덧붙이는 것이다.
(형태소 발생 확률은 수정된 세종 코퍼스에서 계산하였다.) 

통상 확률 태깅 방법이라고 말하면 아래의 bigram 수식을 의미하는데,

<img src="http://www.sciweavers.org/tex2img.php?eq=t_%7B1..n%7D%20%3D%20arg%20max_%7Bt_%7B1..n%7D%7D%20%5Cprod%20P%28w_%7Bi%7D%7Ct_%7Bi%7D%29%20P%28t_%7Bi%7D%7Ct_%7Bi-1%7D%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0" align="center" border="0" alt="t_{1..n} = arg max_{t_{1..n}} \prod P(w_{i}|t_{i}) P(t_{i}|t_{i-1})" width="311" height="28" />

본 사이트에서는 단순히 형태소열이 발생할 확률이 최대인 열을 찾는 모델을 공개한다.
이 이유는 특별한 의미가 있다기보다 모델 사이즈가 작기 때문이다.

<img src="http://www.sciweavers.org/tex2img.php?eq=t_%7B1..n%7D%20%3D%20arg%20max_%7Bt_%7B1..n%7D%7D%20%5Cprod%20P%28w_%7Bi%7D%2Ct_%7Bi%7D%29&bc=White&fc=Black&im=jpg&fs=12&ff=arev&edit=0" align="center" border="0" alt="t_{1..n} = arg max_{t_{1..n}} \prod P(w_{i},t_{i})" width="244" height="28" />

FST를 만든 상태에서 가중치를 추가하는 것은 실제 FST 자체를 변경시키지 않는데,
bigram FST를 위해 품사의 천이 값을 모든 FST에 추가하게 되면 FST의 상태 수가 
크게 증가하는 것을 보게 되었다.
본 실험에서는 실제로 천이 확률 FST도 만들고 형태소 FST와 composition을 해서 
bigram 기반 확률 FST도 만들어 보았는데, unigram FST는 약 50 Mbyte (openfst format)이었고,
bigram FST는 약 600 Mbyte 정도였다.
참고로 Rouzeta 형태소 분석기의 사전 크기는 약 29만이다.

## Rouzeta

[Rouzeta](public/data/rouzeta.tar.gz)의 Rouzeta 폴더에는 아래와 같이 네 개의 파일이 있다.

<pre><code>
shlee@shlee:~/KFST/Rouzeta$ ls
korean.lexc  kormoran.script  morphrules.foma  splithangul.foma  
</code></pre>

[korean.lexc](public/data/korean.lexc.html)는 형태소들과 각 형태소들의 접속 네트워크가 있는
사전이고 (file 크기가 약 6 Mbyte이므로 로딩하는데 시간이 많이 걸린다. 주의 바람), 
[morphrules.foma](public/data/morphrules.foma.html)는 어휘형과 표층형간의 규칙이
적혀 있는 룰 파일이라고 볼 수 있다. [splithangul.foma](public/data/splithangul.foma.html)는 
utf-8 한글 음절을 자소로 분리하는 규칙을 가지고 있으며, 최종적으로 
[kormoran.script](public/data/kormoran.script.html)는 앞의 파일들을 이용하여 최종적으로
하나의 유한 상태 변환기 (finite state transducer)를 만드는 파일이다.

아래를 보면 foma를 수행시킨 후, 'source kormoran.script' 명령어를 넣어서, 
kormoran.script에 있는 스크립트가 수행되는 것을 볼 수 있다.
FST 방식은 룰들을 컴파일하는 과정이기때문에 많은 메모리를 필요로 하고 있으며,
본 실험에서는 약 4분 정도의 컴파일 시간이 걸렸다.
최종적으로 컴파일이 되면, 'up' 명령어를 통해서 표층형에서 어휘형으로 FST를
따라가면서 출력할 수 있게 되는데, 아래 '고마웠다'에 대한 분석 결과로
두 개가 나오는 것을 볼 수 있다.

<pre><code>
apply up> <em><font color="red">고마웠다</font></em>
고맙/irrb/vj었/ep다/ef
고맙/irrb/vj었/ep다/ex
</pre></code>

위에서 '/irrb'는 'ㅂ불규칙'이라는 뜻이고 '/vj'는 형용사, '/ep'는 선어말 어미,
'/ef'는 어말어미, '/ex'는 보조적연결어미이다.
여기서 중요한 것 중 하나는 '/irrb'와 같은 형식들은 모두 하나의 토큰으로 처리된다는 것이다.
내부적으로 한국어는 각 음절이 심벌이고, '/irrb' '/vj'와 같이
불규칙 코드와 품사들은 multi-character symbol이다.


<pre><code>
shlee@shlee: ~/KFST/Rouzeta$ foma
Foma, version 0.9.18alpha (svn r0)
Copyright © 2008-2015 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"
Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.
foma[0]: <em><font color="red">source kormoran.script</font></em>
Opening file 'kormoran.script'.
Root...36, acLexicon...124, acNext...12, adLexicon...5278, adNex
aiLexicon...4, aiNext...8, amLexicon...6, amNext...3, diLexicon.., 
diNext...8, dmLexicon...8, dmNext...11, dnLexicon...185, dnNext..,
duLexicon...17, duNext...5, ecLexicon...1366, ecNext...10, 
...
...
...
pvpoLexicon...1, pvpoNext...1, pvpvLexicon...1, pvpvNext...1,
vxLexicon...94, vxNext...18, xaLexicon...18, xaNext...13, xjLexic..
xjNext...17, xnLexicon...184, xnNext...56, xvLexicon...10, xvNext.
finLexicon...1
Building lexicon...
Determinizing...
Minimizing...
Done!
28.5 MB. 123800 states, 1857280 arcs, Cyclic.
defined Lexicon: 28.5 MB. 123800 states, 1857280 arcs, Cyclic.
Opening file 'splithangul.foma'.
defined CodaChange: 735 bytes. 1 state, 11 arcs, Cyclic.
defined SplitHangul: 110.8 kB. 300 states, 2760 arcs, Cyclic.
Opening file 'morphrules.foma'.
defined AdverbSet: 379 bytes. 2 states, 4 arcs, 4 paths.
defined AdnounSet: 379 bytes. 2 states, 4 arcs, 4 paths.
defined EndingSet: 467 bytes. 2 states, 6 arcs, 6 paths.
defined InterSet: 204 bytes. 2 states, 1 arc, 1 path.
defined NounSet: 643 bytes. 2 states, 10 arcs, 10 paths.
defined ParticleSet: 687 bytes. 2 states, 11 arcs, 11 paths.
defined VerbSet: 423 bytes. 2 states, 5 arcs, 5 paths.
defined AuxSet: 379 bytes. 2 states, 4 arcs, 4 paths.
defined EtcSet: 599 bytes. 2 states, 9 arcs, 9 paths.
defined EHSet: 379 bytes. 2 states, 4 arcs, 4 paths.
defined IrrSet: 525 bytes. 2 states, 7 arcs, 7 paths.
defined NounStringSet: 687 bytes. 2 states, 11 arcs, 11 paths.
defined VerbStringSet: 511 bytes. 2 states, 7 arcs, 7 paths.
defined TagSet: 2.1 kB. 2 states, 45 arcs, 45 paths.
defined TagAndIrrSet: 3.0 kB. 2 states, 65 arcs, 65 paths.
defined RemoveTags: 3.1 kB. 1 state, 66 arcs, Cyclic.
defined Onset: 1.0 kB. 2 states, 19 arcs, 19 paths.
defined Peak: 1.1 kB. 2 states, 21 arcs, 21 paths.
defined FILLC: 203 bytes. 2 states, 1 arc, 1 path.
defined Coda: 1.5 kB. 2 states, 28 arcs, 28 paths.
defined Syllable: 3.2 kB. 4 states, 68 arcs, 11172 paths.
defined KorCha: 1.1 kB. 2 states, 19 arcs, 19 paths.
defined KorMo: 1.1 kB. 2 states, 21 arcs, 21 paths.
defined KorChar: 2.0 kB. 2 states, 40 arcs, 40 paths.
defined CodaOnly: 473 bytes. 2 states, 6 arcs, 6 paths.
defined FilterPT0: 2.2 kB. 6 states, 101 arcs, Cyclic.
defined FilterPT1: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined FilterPS0: 2.1 kB. 6 states, 95 arcs, Cyclic.
defined FilterPS1: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined FilterPO0: 2.2 kB. 6 states, 101 arcs, Cyclic.
defined FilterPO1: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined FilterPV0: 3.4 kB. 9 states, 170 arcs, Cyclic.
defined FilterPV1: 5.6 kB. 6 states, 263 arcs, Cyclic.
defined FilterPA0: 17.6 kB. 12 states, 970 arcs, Cyclic.
defined FilterPA1: 13.8 kB. 9 states, 727 arcs, Cyclic.
defined FilterPC0: 2.1 kB. 6 states, 95 arcs, Cyclic.
defined FilterPC1: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined FilterPC2: 3.2 kB. 9 states, 161 arcs, Cyclic.
defined FilterPC3: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined FilterPX0: 4.2 kB. 12 states, 226 arcs, Cyclic.
defined FilterPX1: 7.6 kB. 9 states, 394 arcs, Cyclic.
defined FilterPX2: 5.0 kB. 13 states, 271 arcs, Cyclic.
defined FilterPX3: 8.5 kB. 10 states, 448 arcs, Cyclic.
defined FilterPX4: 5.9 kB. 15 states, 328 arcs, Cyclic.
defined FilterPX5: 10.3 kB. 12 states, 562 arcs, Cyclic.
defined FilterPX6: 3.2 kB. 9 states, 161 arcs, Cyclic.
defined FilterPX7: 7.8 kB. 9 states, 404 arcs, Cyclic.
defined FilterPX8: 3.4 kB. 9 states, 170 arcs, Cyclic.
defined FilterPX9: 5.5 kB. 6 states, 257 arcs, Cyclic.
defined NounParticleFilter: 79.9 kB. 57 states, 4944 arcs, Cyclic.
defined VerbEndingFilter: 2.0 kB. 6 states, 88 arcs, Cyclic.
defined BrightVowel: 291 bytes. 2 states, 2 arcs, 2 paths.
defined DarkVowel: 1.1 kB. 2 states, 19 arcs, 19 paths.
defined DarkSyllable: 1.6 kB. 4 states, 30 arcs, 28 paths.
defined BrightSyllable: 1.6 kB. 4 states, 30 arcs, 28 paths.
defined BrightVowelHarmony: 34.2 kB. 32 states, 2057 arcs, Cyclic.
defined DarkMinusEU: 2.8 kB. 4 states, 74 arcs, 531 paths.
defined DarkVowelHarmony: 20.3 kB. 14 states, 1134 arcs, Cyclic.
defined EUHarmony: 22.1 kB. 17 states, 1264 arcs, Cyclic.
defined SingleEUSyllable: 8.7 kB. 8 states, 436 arcs, Cyclic.
defined EolaRestriction: 3.0 kB. 11 states, 147 arcs, Cyclic.
defined VowelHarmony: 92.5 kB. 74 states, 5751 arcs, Cyclic.
defined PPFilter: 491 bytes. 3 states, 11 arcs, Cyclic.
defined PPSyllable: 334 bytes. 4 states, 3 arcs, 1 path.
defined NotEo: 1.9 kB. 3 states, 38 arcs, 360 paths.
defined DelPPSyllable: 4.8 kB. 8 states, 201 arcs, Cyclic.
defined ShortenYIPP: 1.7 kB. 8 states, 60 arcs, Cyclic.
defined ShortenYIVB: 6.3 kB. 27 states, 328 arcs, Cyclic.
defined RuleYI: 15.8 kB. 39 states, 882 arcs, Cyclic.
defined MarkVerbEU: 4.4 kB. 10 states, 208 arcs, Cyclic.
defined DropEU: 6.3 kB. 20 states, 330 arcs, Cyclic.
defined InsertEU1: 6.6 kB. 11 states, 312 arcs, Cyclic.
defined InsertEU2: 4.4 kB. 6 states, 182 arcs, Cyclic.
defined InsertEU3: 829 bytes. 6 states, 24 arcs, Cyclic.
defined InsertEU4: 816 bytes. 5 states, 23 arcs, Cyclic.
defined InsertEU: 8.4 kB. 16 states, 425 arcs, Cyclic.
defined IrrConjO: 2.3 kB. 16 states, 115 arcs, Cyclic.
defined DropL: 2.3 kB. 9 states, 99 arcs, Cyclic.
defined DropS: 1.4 kB. 7 states, 56 arcs, Cyclic.
defined IrrConjD: 898 bytes. 7 states, 30 arcs, Cyclic.
defined PhnOnsetCtxt: 511 bytes. 4 states, 7 arcs, 5 paths.
defined PhnCodaCtxt: 338 bytes. 2 states, 3 arcs, 3 paths.
defined ChangeB: 1.6 kB. 9 states, 66 arcs, Cyclic.
defined DeleteBEU: 3.6 kB. 13 states, 175 arcs, Cyclic.
defined IrrConjB: 5.3 kB. 21 states, 282 arcs, Cyclic.
defined MarkIrrl: 3.0 kB. 13 states, 147 arcs, Cyclic.
defined IrrConjl: 6.8 kB. 26 states, 387 arcs, Cyclic.
defined IrrConjL: 1.6 kB. 6 states, 64 arcs, Cyclic.
defined MarkIrru: 2.2 kB. 11 states, 101 arcs, Cyclic.
defined IrrConju: 2.8 kB. 17 states, 135 arcs, Cyclic.
defined IrrConjYEO1: 1.8 kB. 6 states, 78 arcs, Cyclic.
defined IrrConjYEO2: 1.3 kB. 16 states, 46 arcs, Cyclic.
defined IrrConjYEO: 2.3 kB. 20 states, 105 arcs, Cyclic.
defined IrrGeola1: 3.5 kB. 16 states, 181 arcs, Cyclic.
defined IrrGeola2: 1.8 kB. 10 states, 76 arcs, Cyclic.
defined IrrNeola: 2.7 kB. 15 states, 135 arcs, Cyclic.
defined IrrEola: 5.9 kB. 23 states, 331 arcs, Cyclic.
defined ChangeHRule: 4.8 kB. 30 states, 267 arcs, Cyclic.
defined PhnOnsetNLM: 335 bytes. 2 states, 3 arcs, 3 paths.
defined PhnCodaNLM: 338 bytes. 2 states, 3 arcs, 3 paths.
defined ChangeH: 2.5 kB. 13 states, 118 arcs, Cyclic.
defined DeleteHEU1: 1.5 kB. 9 states, 63 arcs, Cyclic.
defined DeleteHEU2: 1.2 kB. 7 states, 47 arcs, Cyclic.
defined DeleteHEU: 1.9 kB. 9 states, 81 arcs, Cyclic.
defined IrrConjH: 10.8 kB. 44 states, 636 arcs, Cyclic.
defined MarkDiphOA: 4.2 kB. 9 states, 182 arcs, Cyclic.
defined MarkDiphUEO: 4.2 kB. 9 states, 181 arcs, Cyclic.
defined MarkDiphWAEO: 2.2 kB. 8 states, 89 arcs, Cyclic.
defined MarkDiphUA: 3.2 kB. 11 states, 151 arcs, Cyclic.
defined MarkDiphAA: 3.1 kB. 11 states, 144 arcs, Cyclic.
defined MarkDiphEOEO: 3.1 kB. 11 states, 144 arcs, Cyclic.
defined MarkDiphOA2: 3.5 kB. 12 states, 172 arcs, Cyclic.
defined MarkDiphUEO2: 3.5 kB. 12 states, 172 arcs, Cyclic.
defined MarkDiph: 27.0 kB. 51 states, 1619 arcs, Cyclic.
defined RuleDiph: 9.0 kB. 29 states, 517 arcs, Cyclic.
defined ConjDiph: 41.4 kB. 72 states, 2532 arcs, Cyclic.
defined ConjEAE: 913 bytes. 12 states, 26 arcs, Cyclic.
defined ChangeNullCoda: 26.2 kB. 27 states, 1478 arcs, Cyclic.
defined ChangeNWA1: 807 bytes. 6 states, 21 arcs, Cyclic.
defined ChangeNWA2: 807 bytes. 6 states, 21 arcs, Cyclic.
defined ChangeSYEO: 1.1 kB. 11 states, 33 arcs, Cyclic.
defined ChangeSYEOS: 805 bytes. 6 states, 21 arcs, Cyclic.
defined ChangeHAEXT: 2.9 kB. 16 states, 143 arcs, Cyclic.
defined ChangeHaji: 861 bytes. 10 states, 21 arcs, Cyclic.
defined ReducedWords: 6.8 kB. 45 states, 371 arcs, Cyclic.
defined AbnormalSequence: 1.0 kB. 21 states, 27 arcs, 8 paths.
defined FilterOut: 5.6 kB. 20 states, 316 arcs, Cyclic.
defined AlternationRules: 26.7 MB. 360257 states, 1750440 arcs, Cy
defined SingleWordPhrase: 42.9 MB. 127415 states, 2797946 arcs, Cy
defined Delim: 202 bytes. 2 states, 1 arc, 1 path.
defined NormalizeDelim: 364 bytes. 2 states, 4 arcs, Cyclic.
defined WPWithMark: 42.9 MB. 127417 states, 2798456 arcs, Cyclic.
defined SentenceWithMark: 42.9 MB. 127417 states, 2798457 arcs, Cy
defined DeleteMarkUp: 376 bytes. 1 state, 3 arcs, Cyclic.
defined DeleteMarkDown: 376 bytes. 1 state, 3 arcs, Cyclic.
defined Sentence: 43.0 MB. 127416 states, 2806708 arcs, Cyclic.
43.0 MB. 127416 states, 2806708 arcs, Cyclic.
foma[1]: <em><font color="red">up</font></em>
apply up> <em><font color="red">고마웠다</font></em>
고맙/irrb/vj었/ep다/ef
고맙/irrb/vj었/ep다/ex
apply up> <em><font color="red">빨개서</font></em>
빨갛/irrh/vj아서/ef
빨갛/irrh/vj아서/ex
빨갛/irrh/vj아/ec서/pa
빨/vb\_ㄹ/ed개서/nc
빨/vb\_ㄹ/ed개/nc서/nc
빨/vb\_ㄹ/ed개/nc서/px
빨/vb\_ㄹ/ed개/nc서/pa
빨/vb\_ㄹ/ed개/nd서/pa
빨/vb\_ㄹ/ed개/nd서/xn
빨/vb\_ㄹ/ed개/nd서/ps
빨/nc개서/nc
빨/nc개/nc서/nc
빨/nc개/nc서/px
빨/vj\_ㄹ/ed개서/nc
빨/vj\_ㄹ/ed개/nc서/nc
빨/vj\_ㄹ/ed개/nc서/px
빨/vj\_ㄹ/ed개/nc서/pa
빨/vj\_ㄹ/ed개/nd서/pa
빨/vj\_ㄹ/ed개/nd서/xn
빨/vj\_ㄹ/ed개/nd서/ps
apply up> <em><font color="red">잡았다</font></em>
잡/vb았/ep다/ef
잡/vb았/ep다/ex
잡/vx았/ep다/ef
잡/vx았/ep다/ex
apply up> <em><font color="red">당신은</font></em>
당신/nc은/nc
당신/nc은/pt
당신/nr은/nc
당신/nr은/pt
당신/np은/nc
당신/np은/pt
당/ad시/vj\_ㄴ/ed은/nc
당/ad시/vj\_ㄴ/ed은/nr
당/ad신/dn은/nc
당/ad신/dn은/nr
당/nc시/vj\_ㄴ/ed은/nc
당/nc시/vj\_ㄴ/ed은/nr
당/nc신/nc은/nc
당/nc신/nc은/pt
당/nc신/dn은/nc
당/nc신/dn은/nr
당/nr신/nc은/nc
당/nr신/nc은/pt
당/dn신/nc은/nc
당/dn신/nc은/pt
당/dn신/nr은/nc
당/dn신/nr은/pt
apply up> <em><font color="red">사괄 먹는다</font></em>
사과/nc\_ㄹ/po 먹/vb는다/ef
사과/nc\_ㄹ/po 먹/vb는다/ex
사과/nc\_ㄹ/po 먹/vx는다/ef
사과/nc\_ㄹ/po 먹/vx는다/ex
사과/nr\_ㄹ/po 먹/vb는다/ef
사과/nr\_ㄹ/po 먹/vb는다/ex
사과/nr\_ㄹ/po 먹/vx는다/ef
사과/nr\_ㄹ/po 먹/vx는다/ex
apply up> <em><font color="red">computer 在家</font></em>
computer/ne 在家/nh
apply up> 
foma[1]: <em><font color="red">exit</font></em>
</pre></code>

(위 실행예는 실제 실행 예보다 많이 줄여서 화면에 보여준 것입니다.)
위 분석 결과를 보면, 생각보다 많은 분석 결과가 나오는 것을 볼 수 있는데,
이는 세종 코퍼스에서 임의의 두 품사가 공백 없이 사용되는 경우,
형태소 천이 네트워크에서 붙여져 표현되기 때문이다.
본인의 생각은, 매우 고빈도로 과분석되어 나오는 경우를 찾아서
이러한 결과가 나오지 않도록 필터를 설계한 후 composition하면
좀 더 나은 형태소 분석 결과가 나올 것으로 예측한다.

최종적으로 만들어진 한국어 형태소 분석 FST의 크기를 보면,
상태의 개수는 127,416개, 상태와 상태를 잇는 아크(arc)의 개수는 
2,806,708개이다. 총 사용된 형태소의 수는 대략 29만개이다.


## Tagger

품사 태깅이라는 것은 주어진 문장에 대해서 가장 맞는 형태소 열을 구하는 문제로 
볼 수 있다. 나는 20년 전에 석사 학위 논문으로 
[미등록어를 고려한 한국어 품사 태깅 시스템 구현](http://zincfunc.cafe24.com/homepage/papers/msthesis.tar.gz)를
구현한 적이 있는데, 그 당시에는 확률에 의한 방법이 가장 합리적이라는 생각을
했었다. 하지만, Emmanuel Roche와 Yves Schabes가 쓴
[Deterministic Part-of-speech tagging with Finite-state Transducers](http://anthology.aclweb.org/J/J95/J95-2004.pdf)를
읽어보고 규칙 기반 방법론에 대해 관심을 가지게 되었고,
Christer Samuelsson이 쓴 [Inducing Constraint Grammars](http://arxiv.org/pdf/cmp-lg/9607002.pdf)를 읽고,
인간이 추론하는 방법에 근접한 방식으로 언어처리 모듈을 작성할 수 있다는 생각이 들었다.

그래서 개인적으로 이번 Rouzeta 형태소 분석기를 만들면서 구현하고 싶었던 것은,
유한 상태 변환기를 기반으로 형태소 분석기를 만들되, 한국어 형태소 열에서
발생할 수 없는 sequence, 즉 특정 열이 존재할 수 없는 '제약 조건 셋'을 구하고
(Inducing Constraint Grammars 논문의 방향성에 맞추어) 이로부터 Constraint FST를 만든 후,
원래의 FST에서 Constraint FST를 뺀 최종 FST를 구하고자 했다.
(이러한 방법론에 대해서 알고 싶은 사람은 [Mehryar Mohri](http://cs.nyu.edu/cs/faculty/mohri/)가 쓴
[Local Grammar Algorithms](http://www.cs.nyu.edu/~mohri/pub/kos.pdf)를 읽어보기 바란다.)
마지막으로 구한 FST에는 아주 간단한 unigram 확률값 <em> P(w<sub>i</sub>, t<sub>i</sub>) </em>만을 부여하여
남아 있는 ambiguity를 해소하고자 했다.

하지만, 이번 과제를 두 달에 걸쳐서 진행하였는데, (세종 코퍼스를 정제하는데 3주 정도가 걸리고 말았다.)
앞으로 더 이 과제를 진행할 시간이 있을 것 같지 않아서 일단 이 정도 수준에서 결과물을
정리하고자 한다. 그러다보니 형태소 분석 FST에 단순히 unigram 확률만 부여하게 되었다.

위에서 구한 Rouzeta 형태소 분석기에 unigram 확률을 부여하는 것은 단순한 일이다.
세종 코퍼스로부터 unigram 확률을 추출하고, 아래와 같은 형식으로 unigram FST를 만든다. 
즉, 글자 심벌에서는 0을 부여하고 품사 심벌이 나오는 곳에 <em> -log P(w<sub>i</sub>, t<sub>i</sub>) </em>를 부여한다.

![unigram 확률이 부착된 단어 FST](public/images/wfst.jpg) 

그 이후, Rouzeta FST와 unigram FST를 composition하면 확률이 부여된 형태소 분석기가 만들어진다.
(좀 더 정확히 이야기하면, Rouzeta FST는 입력이 어휘형이고 출력이 표층형이라서,
Rouzeta FST의 inverse FST와 unigram FST를 composition한다. 이렇게 되면,
입력이 표층형이고 출력이 어휘형, 그리고 확률은 unigram인 최종 
Tagger WFST (Weighted Finite State Transducer)가 만들어진다.)

이렇게 구한 Tagger WFST를 구동시키는 방법은,
입력 문장을 linear FST로 만든 후, 이를 Tagger FST와 composition한 후 minimum distance algorithm
(log의 합이 최소가 되는 path)을 수행한 결과물이 품사 태깅 결과가 된다.
이 방법은 아주 전통적인 방법이라서 대학원 수업에서 
[Homework](http://www.csee.ogi.edu/~sproatr/Courses/CompLing/Homework/homework1.html)으로 나온다.

한편, 이렇게 구해진 WFST를 쉽게 그냥 문장만 넣어서 결과를 볼 수 없을까 고민했는데,
[kyfd](http://www.phontron.com/kyfd/)라는 WFST beam-search decoder가 공개된 것을 발견하게 되었고,
이를 컴파일하여 테스팅해 보았다.
(참고로 kyfd는 openfst 옛날 버전과 컴파일해야 제대로 컴파일되었다.  테스팅을 위해서 컴파일된 kyfd를 함께 포함시킨다.)

아래는 Tagger WFST를 구동시킨 예이다.

<pre><code>
shlee@shlee: ~/KFST/Tagger$ <em><font color="red">cat testme.txt</font></em>
나 는 \<space\> 학 교 에 서 \<space\> 공 부 합 니 다 .
선 을 \<space\> 그 어 \<space\> 버 렸 다 .
고 마 웠 다 .
나 는 \<space\> 답 을 \<space\> 몰 라 .
지 난 \<space\> 1 8 일 \<space\> 하 오 \<space\> 3 시 \<space\> 경 남 \<space\> 마 산 시
색 이 \<space\> 하 얘 서 \<space\> 예 뻤 다 .
일 찍 \<space\> 일 어 나 는 \<space\> 새 가 \<space\> 피 곤 하 다 ( 웃 음 ) .
꽃 이 \<space\> 핀 \<space\> 곳 을 \<space\> 알 고 있 다 .
이 것 은 \<space\> 사 과 다 .
상 자 를 \<space\> 연 \<space\> 사 람 은 \<space\> 그 다 .
사 괄 \<space\> 먹 겠 다 .
향 약 은 \<space\> 향 촌 의 \<space\> 교 육 과 \<space\> 경 제 를 \<space\> 관 장 해 \<space\> 서 원 을 \<space\> 운 영 하 면 서 \<space\> 중 앙 \<space\> 정 부 \<space\> 등 용 문 인 \<space\> 대 과 \<space\> 응 시 자 격 을 \<space\> 부 여 하 는 \<space\> 향 시 를 \<space\> 주 관 하 고 \<space\> 흉 년 이 \<space\> 들 면 \<space\> 곡 식 을 \<space\> 나 누 는 \<space\> 상 호 부 조 와 \<space\> 작 황 에 \<space\> 따 른 \<space\> 소 작 료 \<space\> 연 동 적 용 을 \<space\> 정 하 는 가 \<space\> 하 면 \<space\> 풍 속 사 범 에 \<space\> 대 해 \<space\> 형 벌 을 \<space\> 가 하 는 \<space\> 사 법 부 \<space\> 역 할 까 지 \<space\> 담 당 했 었 다 .

shlee@shlee: ~/KFST/Tagger$ <em><font color="red">cat testme.txt | ./kyfd koreanuni.xml</font></em>
-- Started Kyfd Decoder --
Loaded configuration, initializing decoder...
Loading fst korfinaluni.fst... 
Done initializing, took 0 seconds
Decoding...
나 /np 는 /pt \<space\> 학 교 /nc 에 서 /pa \<space\> 공 부 /na 하 /xv _ㅂ 니 다 /ef . /sf
선 /nc 을 /po \<space\> 긋 /irrs /vb 어 /ex \<space\> 버 리 /vx 었 /ep 다 /ef . /sf
고 맙 /irrb /vj 었 /ep 다 /ef . /sf
나 /np 는 /pt \<space\> 답 /nc 을 /po \<space\> 모 르 /irrl /vb 아 /ec . /sf
지 나 /vb _ㄴ /ed \<space\> 1 8 /nb 일 /nc \<space\> 하 오 /nc \<space\> 3 /nb 시 /nc \<space\> 경 남 /nr \<space\> 마 산 시 /nr
색 /nc 이 /ps \<space\> 하 얗 /irrh /vj 어 서 /ef \<space\> 예 쁘 /vj 었 /ep 다 /ef . /sf
일 찍 /ad \<space\> 일 어 나 /vb 는 /ed \<space\> 새 /nc 가 /ps \<space\> 피 곤 /ns 하 /xj 다 /ef ( /sl 웃 음 /nc ) /sr . /sf
꽃 /nc 이 /ps \<space\> 핀 /nc \<space\> 곳 /nc 을 /po \<space\> 알 /vb 고 /ec 있 /vj 다 /ef . /sf
이 것 /nm 은 /pt \<space\> 사 과 /nc 이 /pp 다 /ef . /sf
상 자 /nc 를 /po \<space\> 연 /nc \<space\> 사 람 /nc 은 /pt \<space\> 그 /np 이 /pp 다 /ef . /sf
사 과 /nc _ㄹ /po \<space\> 먹 /vb 겠 /ep 다 /ef . /sf
향 약 /nc 은 /pt \<space\> 향 촌 /nc 의 /pd \<space\> 교 육 /nc 과 /pc \<space\> 경 제 /nc 를 /po \<space\> 관 장 /nc 해 /nc \<space\> 서 원 /nc 을 /po \<space\> 운 영 /na 하 /xv 면 서 /ef \<space\> 중 앙 /nc \<space\> 정 부 /nc \<space\> 등 용 문 /nc 인 /nc \<space\> 대 과 /nc \<space\> 응 시 자 격 /nc 을 /po \<space\> 부 여 /na 하 /xv 는 /ed \<space\> 향 시 /nc 를 /po \<space\> 주 관 /nc 하 고 /pq \<space\> 흉 년 /nc 이 /ps \<space\> 들 /vb 면 /ex \<space\> 곡 식 /nc 을 /po \<space\> 나 누 /vb 는 /ed \<space\> 상 호 부 조 /nc 와 /pc \<space\> 작 황 /nc 에 /pa \<space\> 따 르 /vb _ㄴ /ed \<space\> 소 작 료 /nc \<space\> 연 동 적 용 /nc 을 /po \<space\> 정 하 /vb 는 가 /ef \<space\> 하 /vb 면 /ex \<space\> 풍 속 사 범 /nc 에 /pa \<space\> 대 하 /vb 어 /ex \<space\> 형 벌 /nc 을 /po \<space\> 가 하 /vb 는 /ed \<space\> 사 법 부 /nc \<space\> 역 할 /nc 까 지 /px \<space\> 담 당 /na 하 /xv 었 었 /ep 다 /ef . /sf
Done decoding, took 0 seconds
</pre></code>

위에서 모든 글자 하나 하나 사이에 공백을 넣었는데, 그 이유는 kyfd가
공백 단위 별로 심벌을 받기 때문인 것 뿐이고, "< space >"라는 표시를 넣은 것은
"< space >"가 실제로 FST에 들어갈 때는 " " 공백으로 들어가게 되기 때문이다.
프로그램을 작성하지 않고 오픈 소스를 사용하려다 보니, 위와 같이 좀 불편하게 사용하게
되었는데, Finite State Transducer에 관심있는 사람은 최종 파일을 처리하는
좀 더 쉬운 프로그램을 작성해도 좋을 것 같다.

위 결과를 보면, 종종 품사 태깅 결과가 틀린 것을 볼 수 있는데, bigram 확률을 부여한 FST로
(사이즈가 600 Mbyte로 커졌지만) 처리를 해 보니, 아래와 같은 결과를 얻었다.
개인적으로는, 이렇게 무식할 정도로, 그리고 ambiguity resolution하는데
크게 필요 없는 context에서도 bigram 확률을 부여하는 것을 좋아하지 않는다.
그래서 bigram 확률을 부여했을 때, unigram 확률 부여 방식과의 차이만 보여주고자
아래에 그 결과를 넣는다.
( 이 사이트에서는 bigram WFST의 크기가 너무 커서 공개하지 않는다.
  아래는 내 컴퓨터에서 실험한 결과를 캡쳐해서 보여준 것 뿐이다. )

<pre><code>
shlee@shlee:~/FST/KFST.1.0/att2$ <em><font color="red">cat testme.txt | ./kyfd koreanbi.xml</font></em>
-- Started Kyfd Decoder --
Loaded configuration, initializing decoder...
Loading fst korinvertwordbifinal.fst... 
Done initializing, took 6 seconds
Decoding...
나 /np 는 /pt \<space\> 학 교 /nc 에 서 /pa \<space\> 공 부 /na 하 /xv _ㅂ 니 다 /ef . /sf
선 /nc 을 /po \<space\> 긋 /irrs /vb 어 /ex \<space\> 버 리 /vx 었 /ep 다 /ef . /sf
고 맙 /irrb /vj 었 /ep 다 /ef . /sf
나 /np 는 /pt \<space\> 답 /nc 을 /po \<space\> 모 르 /irrl /vb 아 /ef . /sf
지 나 /vb _ㄴ /ed \<space\> 1 8 /nb 일 /nu \<space\> 하 오 /nc \<space\> 3 /nb 시 /nu \<space\> 경 남 /nr \<space\> 마 산 시 /nr
색 /nc 이 /ps \<space\> 하 얗 /irrh /vj 어 /ec 서 /pa \<space\> 예 쁘 /vj 었 /ep 다 /ef . /sf
일 찍 /ad \<space\> 일 어 나 /vb 는 /ed \<space\> 새 /nc 가 /ps \<space\> 피 곤 /ns 하 /xj 다 /ef ( /sl 웃 음 /nc ) /sr . /sf
꽃 /nc 이 /ps \<space\> 피 /vb _ㄴ /ed \<space\> 곳 /nc 을 /po \<space\> 알 /vb 고 /ex 있 /vx 다 /ef . /sf
이 것 /nm 은 /pt \<space\> 사 과 /nc 이 /pp 다 /ef . /sf
상 자 /nc 를 /po \<space\> 열 /vb _ㄴ /ed \<space\> 사 람 /nc 은 /pt \<space\> 그 /np 이 /pp 다 /ef . /sf
사 과 /nc _ㄹ /po \<space\> 먹 /vb 겠 /ep 다 /ef . /sf
향 약 /nc 은 /pt \<space\> 향 촌 /nc 의 /pd \<space\> 교 육 /nc 과 /pc \<space\> 경 제 /nc 를 /po \<space\> 관 장 /nc 해 /nc \<space\> 서 원 /nc 을 /po \<space\> 운 영 /na 하 /xv 면 서 /ef \<space\> 중 앙 /nc \<space\> 정 부 /nc \<space\> 등 용 문 /nc 인 /nc \<space\> 대 /nc 과 /pa \<space\> 응 시 자 격 /nc 을 /po \<space\> 부 여 /na 하 /xv 는 /ed \<space\> 향 시 /nc 를 /po \<space\> 주 관 /nc 하 고 /pc \<space\> 흉 년 /nc 이 /ps \<space\> 들 /vb _ㄹ /ed 면 /nc \<space\> 곡 식 /nc 을 /po \<space\> 나 누 /vb 는 /ed \<space\> 상 호 부 조 /nc 와 /pc \<space\> 작 황 /nc 에 /pa \<space\> 따 르 /vb _ㄴ /ed \<space\> 소 작 료 /nc \<space\> 연 동 적 용 /nc 을 /po \<space\> 정 하 /vb 는 /ed 가 /nc \<space\> 하 면 /nr \<space\> 풍 속 사 범 /nc 에 /pa \<space\> 대 해 /nc \<space\> 형 벌 /nc 을 /po \<space\> 가 하 /vb 는 /ed \<space\> 사 법 부 /nc \<space\> 역 할 /nc 까 지 /px \<space\> 담 당 /na 하 /xv 었 었 /ep 다 /ef . /sf
</pre></code>

unigram 확률과 bigram 확률을 이용했을 때의 결과물 차이를 보면,
아무래도 bigram 확률을 사용했을 때 좀 더 정확한 것을 알 수 있다.
"핀 곳을"과 "연 사람은" 두 부분을 보더라도 unigram은 "핀"과 "연"을 모두 체언으로 분석한 반면,
bigram을 이를 "용언+어미" 형식으로 분석하였다.

위에서 보면, 계산하는데 6초가 걸린다고 나오고 있는데, 사실 이것은 메모리로 loading하는
시간 때문인 것이고, FST는 아마 스트링 처리에 있어서 가장 빠른 방법이지 않을까 생각한다.
FST 자체는 그 결과물의 형태가 매우 단순하기 때문에, 해당 모델을 구동시키는 모듈을
쉽게 구현할 수 있다. 그리고 최종 모델의 형식이, 말 그대로 for loop가 있는 
프로그램이라기보다, 노드에서 노드로 천이하는 모델이라서 절차적(procedual)이지 않고
표현적(descriptive)이다. 그래서 우리가 이해하기도 편하다.

### 결론

본 연구는 하나의 궁금증에서 시작되었다. [Xerox](http://www.xerox.com)는 매우 오래전부터
FST를 이용해서 형태소 분석, 품사 태깅, 파싱, 의미 분석 등 다양한 분야에 적용을 시도하였고,
[Linguistic Tools](https://open.xerox.com/Services/fst-nlp-tools/)를 오픈하고 있다.
한편 왠지 한국어 처리에 대해서 FST를 사용하는 경우가 많이 관찰되지 않는다는 느낌이 있었고,
그 이유가 한국어의 특수성 (?) 때문일까라는 생각이 들었다.
그래서 검색을 해 보았으며, 일본어는
[A Morphological Analyzer for Japanese Nouns, Verbs and Adjectives](https://arxiv.org/abs/1410.0291)라는
논문을 찾았고,
한국어에서도 [합성 유한상태전이기를 이용한 two-level 한국어 형태소 해석](http://m.riss.kr/search/detail/DetailView.do?p_mat_type=be54d9b8bc7cdb09&control_no=fe7513336652b81bffe0bdc3ef48d419)이라는 논문을 찾게 되었다.

다만, 검색을 해보아도 한국어 형태소 분석에 필요한 모든 규칙을 유한 상태 변환기로 구현해 놓은 것이
아직까지 공개되지 않았다는 것을 알게 되었으며, 그러한 점에서 이번 연구는 의미가 있다고 본다.
여기에서 공개된 규칙은 직접 하나 하나 작성한 것이고,
사전은 세종 코퍼스에서 추출하였으며, 용언에 필요한 불규칙 코드는 20년 전에 공개했던
[KTS](http://zincfunc.cafe24.com/homepage/programs/kts.tar.gz)에서, 인터넷 검색을 통해서,
그리고 실험하면서 오류를 발견하면 직접 코드를 넣기도 했다.
한자의 경우도 인터넷에 공개된 한자 리스트들을 모았고 세종 코퍼스에서 나오는 한자와 합쳐서 구축하였다.
Rouzeta 형태소 분석기를 사용하는데 (덧붙여 혹시라도 품사 태거를 사용하는 것 포함해서)
가능한한 라이센스에 문제가 없도록 하였으므로, 한국어 형태소 분석기가 필요한 분이거나,
혹은 한국어 어휘 형태론을 연구하시는 분에게 도움이 되었으면 한다.

(이 결과물의 라이센스는 굳이 따지자면 가장 느슨한 라이센스인 [MIT 허가서](https://ko.wikipedia.org/wiki/MIT_허가서)에
따릅니다.
즉 무상으로 제한없이 취급해도 좋고, 대신 저작권자는 소프트웨어에 관해서 아무런 책임을 지지 않습니다.
혹시 제가 이렇게 공개하는 것 자체가 라이센스에 문제가 있다면 알려주시면 감사하겠습니다.

참고로 이 연구는 약 2 개월 동안 [Finite State Morphology](https://www.amazon.com/Finite-State-Morphology-Kenneth-Beesley/dp/1575864347) 책을 읽으면서 구현한 것이라서, 제가 구현한 방식이 일반적으로 통용되는 것인지도
잘 모릅니다. 어쩌면 간단하게 구현할 수 있는 것을 복잡하게 구현했을 수도 있습니다.
혹시라도 나쁜 코드를 인터넷에 공개했다고 비난하지 말아 주셨으면 합니다.

본 글을 작성한 이후로 다시 연구할 기회가 많지 않을 것 같고,
이 형태소 분석기를 수정할 기회도 많지 않을 것 같습니다. 
그러므로 분석기를 더 수정해달라거나 하는 요구 사항은 받지 않겠습니다.)

### 참고문헌

<a name='1'> [1] 이상호, 서정연, 오영환, ["KTS: 미등록어를 고려한 한국어 품사 태깅 시스템"](http://society.kisti.re.kr/sv/SV_svpsbs03VR.do?method=detail&menuid=1&subid=11&cn2=GOHHAK_1995_y1995m06a_195), 제 12회 음성통신 및 신호처리 워크샵 논문집, pp 195-199, 1995. </a>

<a name='2'> [2] 심광섭, 양재형, ["인접 조건 검사에 의한 초고속 한국어 형태소 분석"](http://www.dbpia.co.kr/Journal/ArticleDetail/NODE00617598), 한국어 정보과학회 논문지 : 소프트웨어 및 응용 31권 1호, pp 89-99, 2004. </a>

<a name='3'> [3] 강승식, ["음절 정보와 복수어 단위 정보를 이용한 한국어 형태소 분석"](http://www.riss.kr/search/detail/DetailView.do?p_mat_type=be54d9b8bc7cdb09&control_no=f15022ef763938d6), 서울대학교 공학박사 학위 논문, 1993. </a>

<a name='4'> [4] 양승현, 김영섬, ["부분 어절의 기분석에 기반한 고속 한국어 형태소 분석 방법"](http://www.dbpia.co.kr/Journal/ArticleDetail/NODE00607713), 정보과학회 논문지 : 소프트웨어 및 응용, 27권, 3호, pp 290-301, 2000. </a>

<a name='5'> [5] Ronald M. Kaplan, Martin Kay, [Regular Models of Phonological Rule Systems](http://www.aclweb.org/anthology/J94-3001.pdf), Computational Linguistics 1994. </a>


