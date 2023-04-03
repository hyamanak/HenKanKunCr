import re, jaconv

class HenKanKunCr():
     
     extra_space_cri_list = ['^ +.{2}',
                             '､ ', ' ､',
                             '｡ ', ' ｡',
                             '\( +', ' +\)',
                             '[ぁ-ゖァ-ヴー] +[ぁ-ゖァ-ヴー]',
                             ': $']
     missing_space_cri_list = [
          '[A-Za-z0-9:?!|%$#\)][ぁ-んァ-ンー-龥]',
          '[ぁ-んァ-ンー-龥][A-Za-z0-9?!%$#|\(]',
     ]
     katakana = '[ァ-ン]'
     
     zenkaku_non_jp_chars = '[Ａ-Ｚａ-ｚ０-９：！？＋＊＾％＄＃＠；／｛｝［］（）　]'

     zenkaku_special = '[＞＜＆’”]'
     zenkaku_special_dict = {'＞':'&gt;', '＜':'&lt;', '＆':'&amp;', "’":'&apos;', '”':'&quot;'}

     jp_parenthesis = '[「」『』]'

     segment_status = None

     cho_on_issue_list = None

     def __init__(self, segment, cho_on, mistranslation):
          self.segment = segment
          self.cho_on_list = cho_on
          
          self.mistranslate = mistranslation
          self.set_mistranslate_dict()
          self.set_mistranslate_list()
          
          self.set_mistranslation_in_text()

          self.get_cho_on_issue_list()
          #self.set_segment_status()
          
          if self.has_cho_on_issue():
               self.cho_on_issue_list = self.get_cho_on_issue_list()
               self.fix_cho_on_issue()
               
          if self.has_issue(self.zenkaku_non_jp_chars):
               self.fix_byte_issue()
          
          if self.has_issue(self.zenkaku_special):
               self.fix_zenkaku_special()
          
          if self.has_issue_from_list(self.missing_space_cri_list):
               self.fix_space_issue(self.missing_space_cri_list)
          if self.has_issue_from_list(self.extra_space_cri_list):
               self.fix_space_issue(self.extra_space_cri_list)

          

          #TODO: add API automation: 

     def fix_space_issue(self, regex_list) -> None:
          miss = True if regex_list == self.missing_space_cri_list else False
          for item in regex_list:
               issue_list = self.get_issue_list(item)
               fixed_list = self.get_fixed_missing_space_list(issue_list) if miss else self.get_fixed_extra_space_list(issue_list)
               self.fix_issue(issue_list, fixed_list)
     
     def set_mistranslate_dict(self) -> None:
          mistranslate_dict = {}
          for item in self.mistranslate:
               wrong, right = item.split(',')
               mistranslate_dict[wrong] = right
          self.mistranslate_dict = mistranslate_dict
          
     def set_mistranslate_list(self) -> None:
          self.mistranslate_list = [mistranslate for mistranslate in self.mistranslate_dict.keys()]
          
     def set_mistranslation_in_text(self) -> None:
          self.mistranslation_in_text = self.has_mistranslate(self.mistranslate_list)  

     def set_segment_satus(self) -> None:
          pass
          #self.segment_status = self.get_segment_status()
     
     def has_issue(self, regex):
          return bool(re.search(regex, self.segment))
     
     def has_issue_from_list(self, regex_list):
         return any(self.has_issue(regex) for regex in regex_list)
     
     def get_issue_list(self, regex):
          return re.findall(regex, self.segment)
     
     def get_fixed_extra_space_list(self, issue_list):
          return [item.replace(' ', '') for item in issue_list]

     def get_fixed_missing_space_list(self, issue_list):
          return [item[0] + ' ' + item[1] for item in issue_list]
               
     def fix_issue(self, issue_list, fixed_list) -> None:
          temp_sentence = self.segment
          for issue, fixed in zip(issue_list, fixed_list):
               temp_sentence = temp_sentence.replace(issue, fixed)
          self.segment = temp_sentence

     #sentence = ' あいう  えお か(  adfa  )きく ､けこ: ｡ 
     
     def fix_byte_issue(self) -> None:
          self.segment = jaconv.z2h(self.segment, ascii=True, kana=False, digit=True)
     
     def get_zenkaku_special_issue(self) -> list:
          return [key for key in self.zenkaku_special_dict.keys() if key in self.segment]
     
     def fix_zenkaku_special(self) -> None:
          for item in self.zenkaku_special_issue_list:
               self.segment = self.segment.replace(item, self.zenkaku_special_dict[item])
     
     def has_mistranslate(self, mis_list) ->bool:
          return any(item in self.segment for item in mis_list)
     
     def get_mistranslation_in_text(self) -> list:
          return [key for key in self.mistranslate_dict.keys() if key in self.segment]
     
     def fix_mistranslation(self) -> None:
          for item in self.mistranslate_list:
               self.segment = self.segment.replace(item, self.mistranslate_dict[item])
     
     def has_cho_on_issue(self) -> bool:
           return any(re.search(item + '[^ー]|' + item + '$', self.segment) for item in self.cho_on_list)
     
     def get_cho_on_issue_list(self) -> list:
          return [found_item for item in self.cho_on_list for found_item in re.findall(item+'[^ー]|'+item+'$', self.segment)]
                    
     def fix_cho_on_issue(self) -> None:
          for item in self.cho_on_issue_list:
               if re.search(self.katakana, item[-1]):
                    with_cho_on = item + 'ー'
               else:
                    with_cho_on = str(item[:-1]) +'ー' + str(item[-1])
               self.segment = self.segment.replace(item, with_cho_on)
          return self.segment

with open('sample.xliff', 'r', encoding='utf-8') as input, open('mistranslation.txt', 'r', encoding='utf-8') as mistra, open('cho_on.txt', 'r', encoding='utf-8') as cho_on, open('output.xliff', 'a+', encoding='utf-8') as output:
     mistranslations = mistra.read().splitlines()
     cho_on = cho_on.read().splitlines()
     
     target_tag = '<target state='
     target_regex = r'(.*?)(<target state=.*?>)(.*?)(</target>)'
     ##group(1) space or tab
     ##group(2) <target state=.*?>
     ##group(3) text between tags
     ##group(4) close tag     
     
     for line in input:
          if target_tag in line:
               target_text = re.search(target_regex, line)
               #print(target_text)
               henkan = HenKanKunCr(target_text.group(3), cho_on, mistranslations)
               print(target_text.group(1) + target_text.group(2) + henkan.segment + target_text.group(4), file=output)
          else:
               print(line, file=output, end='')
     
     
     