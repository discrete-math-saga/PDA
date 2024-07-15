import re
from cfg import CFG
from stack import Stack
from typing import NamedTuple


class TR(NamedTuple):
    """
    This is used when converting NPDA to CFG.
    [fst]: f and t of NPDA, s is Stack character
    """
    f:str
    S:str|None
    t:str|None

    def __str__(self) -> str:
        s =f'[{self.f}{self.S}{self.t}]'
        if self.f == self.S and self.f == self.t:
            s = f'{self.f}'
        if self.S is None:
            s = f'{self.f}'
        return s


class DPDA:
    """
    Deterministic Pushdown Automaton
    """
    
    def __init__(self, q_0 : str, delta : dict[tuple[str,str,str],tuple[str,list[str]]], F : set[str], Z_0 :str) -> None:
        """
        Constructor

        Parameters
        ---
        q_0 Initial state

        delta Transition function

        F Acceptance state
        
        Z_0 Stack bottom symbol
        """
        self._q_0: str = q_0
        self._delta: dict[tuple[str, str, str], tuple[str, list[str]]] = delta
        self._F: set[str] = F
        self._Z_0: str = Z_0
        states:set[str] = set()
        alphabet:set[str] = set()
        stackAlphabet:set[str] = set()
        for f in delta:
            (q,a,g) = f
            states.add(q)
            if len(a) > 0:
                alphabet.add(a)
            stackAlphabet.add(g)
            (p,AList) = delta[f]
            states.add(p)
            if len(AList) > 0:
                for a in AList:
                    stackAlphabet.add(a)
        self._states: set[str] = states
        self._alphabet: set[str] = alphabet
        self._stackAlphabet: set[str] = stackAlphabet

    def read(self, input : str, latex = False) -> tuple[bool, str, list[str]]:
        """
        Process an input

        Parameters
        ---
        input Input string

        latex True if the output is in LaTeX format

        
        Returns
        ---
        (result,message,sequence)

        result True if the input is accepted

        message Message for the result

        sequence Sequence of state transitions
        """
        q: str = self._q_0
        sequence:list[str] = list()#Sequence of state transitions
        stack:Stack[str] = Stack()
        stack.push(self._Z_0)
        return self._readSub(q,input,sequence,stack,latex)

    def _readSub(self, q : str, inputStr : str, sequence : list[str], stack : Stack[str], latex:bool) -> tuple[bool, str, list[str]]:
        """
        Recursive method for input
        """
        if len(inputStr) == 0:# No more input
            if stack.is_empty():# stack is empty
                ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
                sequence.append(ss)
                message = 'accepted'
                result = True
                if q not in self._F:
                    message = f'stop at {q}'
                    result = False
                return result,message,sequence
            else:# stack is not empty
                ss: str = DPDA._mkStr(q,sequence,inputStr,stack,latex)
                sequence.append(ss)
                g: str = stack.pop()
                f:tuple[str,str,str] = (q,'',g)
                if f not in self._delta:
                    message = f'delta({f}) is not defined'
                    result = False
                    return result,message,sequence
                (q,Z) = self._delta[f]
                DPDA._stackPush(Z,stack)
                return self._readSub(q,inputStr,sequence,stack,latex)
        
        if stack.is_empty():# stack is empty
            ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
            sequence.append(ss)
            message = 'vacant stack'
            result = False
            return result,message,sequence
        
        s: str = inputStr[0]
        ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
        sequence.append(ss)
        g = stack.pop()
        f = (q,s,g)
        if f not in self._delta:
            message = f'delta({f}) is not defined'
            result = False
            return result,message,sequence
        (q,Z) = self._delta[f]
        DPDA._stackPush(Z,stack)
        return self._readSub(q,inputStr[1:],sequence,stack,latex)

    def __str__(self) -> str:
        text: str = f'Q = {self._states}\n'
        text = f'F = {self._F}\n'
        text += f'alphabet = {self._alphabet}\n'
        text += f'stackAlphabet = {self._stackAlphabet}\n'
        text += f'q_0 {self._q_0}\n'
        text += f'Z {self._Z_0}\n'
        text += f'delta {self._delta}\n'
        return text
        
    def latexExp(self) -> str:
        text = DPDA._latexElement('Q',self._states)
        text += DPDA._latexElement('F',self._F)
        text += DPDA._latexElement('\\Sigma',self._alphabet,True)
        text += DPDA._latexElement('\\Gamma',self._stackAlphabet)
        for e in self._delta.keys():
            (q,a,s) = e
            text += f'\\delta\\left({q},{DPDA._toText(a)},'
            if len(s) == 0:
                text += '\\epsilon'
            else:
                for ss in s:
                    text += f'{ss}'
#                    text += f'{DPDA._toText(ss)}'
            text += '\\right)&=\\left('
            (p, s) = self._delta[e]
            text += f'{q},'
            if len(s) == 0:
                text += '\\epsilon'
            else:
                for ss in s:
                    text += f'{ss}'
#                    text += f'{DPDA._toText(ss)}'
            text += '\\right)\\\\\n'
        return text


    @staticmethod
    def _latexElement(name:str,input:set[str],b=False)->str:
        text = f'{name}&=\\set{{'
        for s in input:
            if b:
                text += DPDA._toText(s)+','
            else:
                text += f'{s},'                
        text = text.removesuffix(',')
        text += '}\\\\\n'
        return text

    @staticmethod
    def _toText(s:str)->str:
        s = f'text{{{s}}}'
        return '\\'+re.sub(r'text{(\S+)_(\S+)}',r'text{\1}_{\2}',s)

    @staticmethod
    def _mkStr(q:str,sequence:list[str],inputStr:str,stack:Stack[str],latex:bool) -> str:
        ss:str = ''
        if len(sequence) > 0:
            if latex:
                ss = '\\vdash'
            else:
                ss = '|-'
        if latex:
            if len(inputStr) > 0:
                ss += f'\\left({q},\\text{{{inputStr}}},{DPDA._mkStackStr(stack,latex)}\\right)'
            else:
                ss += f'\\left({q},\\epsilon,{DPDA._mkStackStr(stack,latex)}\\right)'
        else:
            ss += f'({q},{inputStr},{DPDA._mkStackStr(stack,latex)})'
        return ss

    @staticmethod
    def _mkStackStr(stack:Stack[str],latex:bool) -> str:
        reversedStack:Stack[str] = stack.reversed()
        if latex:
            if not reversedStack.is_empty():
                # ss:str = "".join(reversedStack)
                s:str = f'{reversedStack}'
#                s = f'\\text{{{ss}}}'
            else:
                s = '\\epsilon'
        else:
            s = str(reversedStack)
        return s

    @staticmethod
    def _stackPush(Z:list[str],stack:Stack[str]) -> None:
        ZZ = list(reversed(Z))
        for z in ZZ:
            stack.push(z)

    @property
    def states(self) -> set[str]:
        return self._states

    @property
    def alphabet(self) -> set[str]:
        return self._alphabet

    @property
    def stackAlphabet(self) -> set[str]:
        return self._stackAlphabet

    @property
    def F(self) -> set[str]:
        return self._F

    @property
    def delta(self) -> dict[tuple[str, str, str], tuple[str, list[str]]]:
        return self._delta
        
    @property
    def q_0(self) -> str:
        return self._q_0

    @property
    def Z(self) -> str:
        return self._Z_0

################################################################
class NPDA(DPDA):
    """
    Non-deterministic Pushdown Automaton
    """
    def __init__(self, q_0 : str, delta : dict[tuple[str,str,str],list[tuple[str,list[str]]]], F : set[str], Z_0 :str) -> None:
        """
        Constructor

        Parameters
        ---
        q_0 Initial state

        delta Transition function

        F Acceptance state
        
        Z_0 Stack bottom symbol
        """
        self._q_0:str = q_0
        self._delta: dict[tuple[str,str,str],list[tuple[str,list[str]]]] = delta
        self._F: set[str] = F
        self._Z_0: str = Z_0
        states: set[str] = set()
        alphabet: set[str] = set()
        stackAlphabet: set[str] = set()
        for f in delta:
            (q,a,g) = f
            states.add(q)
            if len(a) > 0:
                alphabet.add(a)
            stackAlphabet.add(g)
            for entry in delta[f]:
                (p,l) = entry
                states.add(p)
                if len(l) > 0:
                    for gg in l:
                        stackAlphabet.add(gg)

        self._states: set[str] = states
        self._alphabet: set[str] = alphabet
        self._stackAlphabet: set[str] = stackAlphabet

    def read(self, input : str, latex = False) -> list[tuple[bool, str, list[str]]]:
        q: str = self._q_0
        sequence: list[str] = list()#Sequence of state transitions
        sequenceList: list[tuple[bool,str,list[str]]] = list()
        stack: Stack[str] = Stack()
        stack.push(self._Z_0)
        self._readSub(q,input,sequence,stack,sequenceList, latex)
        return sequenceList

    #再帰的の文字を読む
    def _readSub(self, q:str, inputStr:str, sequence:list[str],stack:Stack[str], sequenceList:list[tuple[bool,str,list[str]]], latex:bool) -> None:
        if len(inputStr) == 0:#No more  input
            if stack.is_empty():#stack is empty
                ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
                sequence.append(ss)
                message = 'accepted'
                result = True
                if len(self._F) > 0:# Acceptance states are defined
                    if q not in self._F:
                        message = f'stop at {q}'
                        result = False
                sequenceList.append((result,message,sequence))
                return
            else:# stack is not empty
                ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
                sequence.append(ss)
                g = stack.pop()
                f = (q,'',g)
                if f not in self._delta:
                    message = f'delta({f}) is not defined'
                    result = False
                    sequenceList.append((result,message,sequence))
                    return
                for o in self._delta[f]:
                    (q,Z) = o
                    newSequence = list(sequence)
                    newStack = Stack(stack)
                    DPDA._stackPush(Z,newStack)
                    self._readSub(q,inputStr,newSequence,newStack,sequenceList,latex)
                return
        
        if stack.is_empty():# stack is empty
            ss = DPDA._mkStr(q,sequence,inputStr,stack,latex)
            sequence.append(ss)
            message = 'vacant stack'
            result = False
            sequenceList.append((result,message,sequence))
            return
        
        s: str = inputStr[0]
        ss: str = DPDA._mkStr(q,sequence,inputStr,stack,latex)
        sequence.append(ss)
        g: str = stack.pop()
        f: tuple[str, str, str] = (q,s,g)
        if f not in self._delta:
            message: str = f'delta({f}) is not defined'
            result = False
            sequenceList.append((result,message,sequence))
            return
        for o in self._delta[f]:
            (q,Z) = o
            newSequence = list(sequence)
            newStack = Stack(stack)
            DPDA._stackPush(Z,newStack)
            self._readSub(q,inputStr[1:],newSequence,newStack,sequenceList,latex)

    def latexExp(self) -> str:
        text: str = DPDA._latexElement('Q',self._states)
        text += DPDA._latexElement('F',self._F)
        text += DPDA._latexElement('\\Sigma',self._alphabet,True)
        text += DPDA._latexElement('\\Gamma',self._stackAlphabet)
        for e in self._delta.keys():
            (q,a,s) = e
            text += f'\\delta\\left({q},{DPDA._toText(a)},'
            if len(s) == 0:
                text += '\\epsilon'
            else:
                for ss in s:
                    text += f'{ss}'
#                    text += f'{DPDA._toText(ss)}'
            text += '\\right)&=\\set{'
            outputs: list[tuple[str, list[str]]] = self._delta[e]
            for (p,s) in outputs:
                text += '\\left('
                text += f'{q},'
                if len(s) == 0:
                    text += '\\epsilon'
                else:
                    for ss in s:
                        text += f'{ss}'
#                        text += f'{DPDA._toText(ss)}'
                text += '\\right),'
            text = text.removesuffix(',')
            text += '}\\\\\n'
        return text

    def toCfg(self) -> CFG:
        """
        Convert this NPDA to CFG in Greibach normal form
        """
        P:dict[TR,list[list[TR]]] = dict()
        # Initial rule
        S = TR('S','S','S')
        P[S] = list()
        for q in self._states:
            P[S].append([TR(self._q_0, self._Z_0, q)])
        
        # Convert transition functions to production rules
        for k in self._delta.keys():# an element of transition functions
            (q, a, A) = k# variables of transition functions, state q, alphabet a, stack alphabet A
            for v in self._delta[k]:
                (q1, pushList) = v# destination state q1, stack push list pushList
                if len(pushList) == 0:# if pushList is empty
                    key = TR(q, A, q1)
                    if not (key in P.keys()):
                        P[key]=list()
                    P[key].append([TR(a,None,None)])
                else:
                    for qLast in self._states:
                        key = TR(q, A, qLast)
                        if not (key in P.keys()):
                            P[key]=list()
                        pushListDummy = list(pushList)
                        self._push2N(key, [TR(a,None,None)], P[key], q1, qLast,pushListDummy,P)
        self._temporaryP = P
        tKeys = NPDA._removeUnterminated(P,S)
        # pprint.pprint(P)
        PP = NPDA._createNewP(P,tKeys)
        return CFG(PP,str(S))


    def _push2N(self, k:TR, output:list[TR], outputList:list[list[TR]], q:str, qLast:str, pushList:list[str],P:dict[TR,list[list[TR]]]) -> None:
        S = pushList[0]
        if len(pushList) == 1:
            output.append(TR(q,S,qLast))
            outputList.append(output)
            # pprint.pprint(P)
            return

        for p in self._states:
            newOutput=list(output)
            newOutput.append(TR(q, S, p))
            self._push2N(k,newOutput,outputList,p,qLast,pushList[1:],P)


    @staticmethod
    def _copyP(P:dict[TR,list[list[TR]]]) -> dict[TR,list[list[TR]]]:
        PP:dict[TR,list[list[TR]]] = dict()
        for k in P.keys():
            dList: list[list[TR]] = P[k]
            PP[k]=list()
            for d in dList:
                PP[k].append(d)
        return PP
    
    @staticmethod
    def _removeUnterminated(P:dict[TR,list[list[TR]]],S:TR) -> set[TR]:
        """
        生成規則の左辺の非終端記号からから終端記号くものだけを残す
        """
        #生成規則のダミーを作る
        PP:dict[TR,list[list[TR]]] = NPDA._copyP(P)
        keys = PP.keys()
        tKeys:set[TR] = set()
        tKeys.add(S)#開始記号は登録する
        while True:
            for k in keys:#右辺が終端記号だけのものを抽出
                lList  = PP[k]
                terminate = False
                for dl in lList:
                    if len(dl) == 0:
                        terminate = True
                    if (len(dl)==1) and (dl[0].S is None):
                        terminate = True
                if terminate:#終端記号を導くものを登録する
                    tKeys.add(k)
                    PP[k]=[[]]#ダミー生成規則の右辺の空にする
            # pprint.pprint(PP)
            find = False
            #まだ、終端記号へと至ると分からない記号を確認
            for k in keys:
                if not (k in tKeys):
                    dList = PP[k]
                    for dll in dList:
                        dl = list(dll)
                        for kt in tKeys:
                            if kt in dl:
                                dl.remove(kt)
                        if (len(dl)==1) and (dl[0].S is None):
                            #右辺には全て終端記号へ至る非終端記号
                            PP[k]=[[]]
                            tKeys.add(k)
                            find=True
                    
            if not find:#新たな終端記号を導く非終端記号は見つからない
                break#終了

        return tKeys

    @staticmethod
    def _createNewP(P:dict[TR,list[list[TR]]],tKeys:set[TR]) -> dict[str, list[list[str]]]:
        """
        三組TRを文字列化し、CFGクラスのコンストラクタに渡せる形とする
        """
        PP:dict[str,list[list[str]]] = dict()
        # pprint.pprint(P)
        for kk in P.keys():
            if kk in tKeys:
                k = str(kk)
                PP[k]=list()
                for dList in P[kk]:
                    accept=True
                    for d in dList:
                        if d.S and (not (d in tKeys)):#右辺に終端記号至らない記号がある
                            accept = False
                    if accept:#終端記号を導く場合も生成規則として記録
                        tmpList:list[str]=list()
                        for d in dList:
                            tmpList.append(str(d))
                        PP[k].append(tmpList)
        return PP

    @property
    def temporaryP(self) -> None:
        pass
    @temporaryP.getter
    def temporaryP(self) -> dict[TR, list[list[TR]]]:
        return self._temporaryP