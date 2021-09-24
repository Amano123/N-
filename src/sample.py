#%%
from typing import Any, List, Tuple
import os
import io
import re
from tqdm import tqdm
from rdflib import Graph
from rdflib.term import URIRef
from rdflib.term import Literal
#%%
class N_Triple_Cleaning():
    def split_n_triple(self, string_triple: str) -> tuple[str, str, str]:
        subj: str = "" # Subject
        pred: str = "" # Predicate
        obje: str = "" # Object
        graph_parse: Graph = Graph().parse(data=string_triple)
        for s,p,o in graph_parse.triples((None, None, None)):
            subj = s
            pred = p
            obje = o
        return subj, pred, obje

    def subject(self, string: str) -> Tuple[str, bool]:
        '''
        Subject cleaning function
        ほとんどの入力が "http://www.wikidata.org/entity/Qxxx" である
        input: str "http://www.wikidata.org/entity/Q31"
        output: str "Q31"
        '''
        pattern: re.Pattern = re.compile(r"^Q\d{1,}")
        item_identifer: str = ""
        literal_flag: bool = False
        # URLならheaderを削除
        if type(string) == URIRef:
            item_identifer = string[string.rfind('/') + 1:]
        elif type(string) == Literal:
            item_identifer = string
        # 正規表現とのマッチング
        if pattern.search(item_identifer):
            # マッチすればTrue
            literal_flag: bool = True

        return item_identifer, literal_flag

    def predicate(self, string: str) -> Tuple[str, bool]:
        """
        predicate cleaning finction
        入力は "Label" と "predicate" を示すURL
        input: str "http://www.w3.org/2000/01/rdf-schema#label"
        poutput: str "rdf-schema#label"
        """
        pattern: re.Pattern = re.compile(r"^P\d{1,}")
        item_identifer: str = ""
        literal_flag: bool = False
        # URLならheaderを削除
        if type(string) == URIRef:
            item_identifer = string[string.rfind('/') + 1:]
        elif type(string) == Literal:
            item_identifer = string
        # 正規表現とのマッチング
        if pattern.search(item_identifer):
            # マッチすればTrue
            literal_flag: bool = True

        return item_identifer, literal_flag

    def object(self, string: str) -> Tuple[str, bool]:
        """
        Obuject cleaning finction
        入力は "Label" と "Obuject" を示すURL
        input: str "http://www.wikidata.org/entity/Qxxx"
        poutput: str "Q123" or strings
        """    
        pattern: re.Pattern = re.compile(r"^Q\d{1,}")
        item_identifer: str = ""
        literal_flag: bool = False
        # URLならheaderを削除
        if type(string) == URIRef:
            item_identifer = string[string.rfind('/') + 1:]
        elif type(string) == Literal:
            item_identifer = string
        # 正規表現とのマッチング
        if pattern.search(item_identifer):
            # マッチすればTrue
            literal_flag: bool = True

        return item_identifer, literal_flag

    def triple(
        self, 
        suject_string: Any, 
        predicate_string: Any, 
        object_string: Any
        ) -> Tuple[List[str], List[bool]]:
        sub, sub_flag = self.subject(suject_string)
        pre, pre_flag = self.predicate(predicate_string)
        obj, obj_flag = self.object(object_string)
        triple: List[str] = [sub, pre, obj]
        triple_flag: List[bool] = [sub_flag, pre_flag, obj_flag]
        return triple, triple_flag
    
    def cleaning_n_triple(self, n_triple) -> Tuple[List[str], List[bool]]:
        subj, pred, obje = self.split_n_triple(n_triple)
        triple, triple_flag = self.triple(subj, pred, obje)
        return triple, triple_flag
    
    def __call__(self, n_triple: str) -> Tuple[List[str], List[bool]]:
        triple, triple_flag = self.cleaning_n_triple(n_triple)
        return triple, triple_flag 

#%%
class N_Triple_Save():
    def __init__(self, path_save_file: str, file_name: str = "wikidata", delimiter: str = "\t") -> None:
        self.path_save_file: str = path_save_file
        os.makedirs(self.path_save_file, exist_ok=True)
        self.file_name_triple: str = f"{file_name}_triple.nt"
        self.file_name_label: str = f"{file_name}_label.nt"
        self.file_open_triple: io.TextIOWrapper = io.open(
            f"{self.path_save_file}/{self.file_name_triple}",
            mode="w"
            )
        self.file_open_label: io.TextIOWrapper = io.open(
            f"{self.path_save_file}/{self.file_name_label}",
            mode="w"
            )
        self.delimiter = delimiter
    
    def write(self, f: io.TextIOWrapper, write_data: List[str]):
        f.write(f"{self.delimiter}".join(write_data) + "\n")

    def close(self):
        self.file_open_triple.close()
        self.file_open_label.close()

    def decide_save_file_path(self, triple_flag: List[bool]) -> Tuple[io.TextIOWrapper, bool]:
        """
        tripleかlabelを判別する関数
        """
        need_edit_flag: bool = False
        open_file: io.TextIOWrapper
        if all(triple_flag):
            open_file = self.file_open_triple
        else :
            open_file = self.file_open_label
            need_edit_flag = True
        return open_file, need_edit_flag
    
    def edit_predicate(self, triple: Any) -> Tuple[List[str], bool]:
        subj: str = triple[0]
        pred: str = triple[1]
        objc = triple[2]
        pattern: re.Pattern = re.compile(r"^P\d{1,}")
        new_pred: str = ""
        continue_flag: bool = False
        # Predicateが"P"から始まるか
        if not pattern.search(pred):
            # 必要なlabel-Predicateは"rdf-schema#label"と"core#altLabel"
            if "rdf-schema#label" in pred or "core#altLabel" in pred:
                split_pred = pred.split("#")
                new_pred = split_pred[1] + "@" + objc.language
            # それ以外は、必要ないので、フラグを立てる
            else :
                continue_flag = True
        # Predicateが"P"から始まるものはそのまま
        else: 
            new_pred = pred

            

        return [subj, new_pred, objc], continue_flag


#%%
class N_Triple():
    def __init__(self, wikidata_path:str, output_file_name: str) -> None:
        self.wikidata_path: str = wikidata_path
        self.cleaning = N_Triple_Cleaning()
        self.save = N_Triple_Save(output_file_name)

    def __call__(self) -> None:
        continue_flag: bool = False
        with open(self.wikidata_path, mode="r") as nt_f:
            for num, n_triple in tqdm(enumerate(nt_f), total=1166571736):
                # # Debug
                # if num > 10000:
                #     break
                triple, triple_flag = self.cleaning(n_triple)
                save_file_open, need_edit_flag = self.save.decide_save_file_path(triple_flag)
                if need_edit_flag:
                    triple, continue_flag = self.save.edit_predicate(triple)
                if continue_flag:
                    continue
                self.save.write(save_file_open, triple)
        self.save.close()

#%%
wikidata_path: str = "data/wikidata.nt"
output_file_name: str = "./test"
n_triple = N_Triple(wikidata_path, output_file_name)
n_triple()
    # %%

# %%

# %%
