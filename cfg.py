from pdaClass import NPDA
class CFG:
    """
    文脈自由文法: Greibach標準形
    """

    def __init__(self, P:dict[str,list[list[str]]], S:str):
        self._P = P
        self._S = S
        self._getAlphabet()
        
    def _getAlphabet(self) -> None:
        self._alphabet:set[str] = set()
        self._N:set[str] = set()
        for k in self._P:
            for entry in self._P[k]:
                if len(entry) == 1:
                    self._alphabet.add(entry[0])
                elif len(entry) > 1:
                    for s in entry[1:]:
                        self._N.add(s)

    def toPda(self) -> NPDA:
        """
        空スタックで受理するNPDAへの変換
        """
        q = 'q'
        delta:dict[tuple[str,str,str],list[tuple[str,list[str]]]] = dict()
        for k in self._P:
            for entry in self._P[k]:
                key: tuple[str, str, str] = (q, entry[0], k)
                if len(entry) == 1:
                    if not (key in delta.keys()):
                        delta[key] = list()
                    delta[key].append((q, []))
                elif len(entry) >1:
                    if not (key in delta.keys()):
                        delta[key]=list()
                    delta[key].append((q, entry[1:]))
                
        return NPDA(q, delta, set(), self._S)

    @property
    def P(self) -> dict[str, list[list[str]]]:
        return self._P
    @property
    def N(self) -> set[str]:
        return self._N
    @property
    def S(self) -> str:
        return self._S