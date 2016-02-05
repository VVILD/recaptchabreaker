from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import re
import os
import sys
import time
import random
import requests
from PIL import Image
 
class capcha_resolver:
    def __init__(self, captchakey, proxy = None):
        """
       It is assumed that you have phantomjs installed into /bin folder on your linux system.
       """
 
        self.TWOCAPTCHA_API_KEY = 'write your key here'
        phantom_args = []
        if proxy:
            self.PROXY = proxy
            phantom_args = ['--proxy='+self.PROXY, '--proxy-type=http', '--proxy-type=https']
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(20)
 
    def fail(self, msg):
        print("[!] Error: " + msg)
        self.driver.save_screenshot('error.png')
 
    def get_page(self):
        self.driver.get('https://www.google.com/recaptcha/api2/demo')
        self.driver.save_screenshot('page.png')
        return 0
 
    def send_capcha(self, filename):
        numbers = []
        captchafile = {'file': open(filename, 'rb')}
        data = {'key': self.TWOCAPTCHA_API_KEY, 'method': 'post'}
        r = requests.post('http://2captcha.com/in.php', files=captchafile, data=data)
        if r.ok and r.text.find('OK') > -1:
            reqid = r.text[r.text.find('|')+1:]
            print("[+] Capcha id: "+reqid)
            for timeout in range(40):
                r = requests.get('http://2captcha.com/res.php?key={0}&action=get&id={1}'.format(self.TWOCAPTCHA_API_KEY, reqid))
                if r.text.find('CAPCHA_NOT_READY') > -1:
                    print(r.text)
                    time.sleep(3)
                if r.text.find('ERROR') > -1:
                    return []
                if r.text.find('OK') > -1:
                    return list(r.text[r.text.find('|')+1:])
        return []
 
    def bypass_captcha(self):
        """
       Google recaptcha could be found by id. Frame with checkbox has id which starts with I0, recapcha frame has id with I1
       """
 
        capthcaboxframe = self.driver.find_element_by_xpath('//iframe[starts-with(@src, "https://www.google.com/recaptcha/api")]')
        self.driver.switch_to.frame(capthcaboxframe)
        time.sleep(1)
        checkbox = self.driver.find_element_by_class_name('recaptcha-checkbox-checkmark')
        checkbox.click()
        print("[*] Clicked on checkbox")
        time.sleep(2)
        self.driver.switch_to.default_content()
 
        capcthaframe = self.driver.find_element_by_xpath('//iframe[starts-with(@src, "https://www.google.com/recaptcha/api2/frame")]')

 
        bounding_box = (
            capcthaframe.location['x'], # left
            capcthaframe.location['y'], # upper
            (capcthaframe.location['x'] + capcthaframe.size['width']), # right
            (capcthaframe.location['y'] + capcthaframe.size['height'])) # bottom
        imgname = 'capcha.jpeg' #use jpeg because png images can exceed 2capcha file size limit
        time.sleep(2)
        self.driver.save_screenshot('test.jpeg')
        base_image = Image.open('test.jpeg')
        cropped_image = base_image.crop(bounding_box)
        base_image = base_image.resize(cropped_image.size)
        base_image.paste(cropped_image, (0, 0))
        base_image.save(imgname)
 
        numbers = self.send_capcha(imgname)
        if numbers == []:
            return -1
        print(numbers)
        #numbers=[1,2]
        result=numbers
        captcha_solving = True
        while captcha_solving:
            try:
                self.driver.switch_to.default_content()
                iframe = self.driver.find_element_by_xpath("//iframe[@title='recaptcha challenge']")
                left_iframe = iframe.location['x']
                top_iframe = iframe.location['y']
                if top_iframe < 0:
                    raise Exception("IFRANE_NOT_LOADED")

                self.driver.switch_to.frame(iframe)
            except Exception as err:
                print("CANNOT_SWITCH_TO_IFRAME: Probably already at it")
            try:
                self.driver.find_element_by_class_name("rc-image-tile-3")
                save_element_screen_shot("rc-imageselect-challenge", "captcha.jpg", captcha_size)
                print("3x3")
            except Exception as err:
                try:
                    self.driver.find_element_by_class_name("rc-image-tile-4")
                    save_element_screen_shot("rc-imageselect-challenge", "captcha.jpg", big_captcha_size)
                    print("4x4")
                except Exception as err2:
                    print("not puzzle captcha")
            try:
                instructions = self.driver.find_element_by_xpath("//div[@class='rc-imageselect-desc-no-canonical']").text
            except Exception as err:
                instructions = self.driver.find_element_by_xpath("//div[@class='rc-imageselect-desc']").text
            print(instructions)
            # result = captchaUpload.solve_recaptcha_text('captcha.jpg', instructions)
            # print(result)
            # try:
            #     result = result.split(":")[1].split("/")
            # except Exception as err:
            #     print("BAD_REQUEST: 2captcha denied image")
            #     self.driver.find_element_by_id("recaptcha-reload-button").click()
            #     continue
            # print(result)
            tiles = self.driver.find_elements_by_class_name("rc-image-tile-target")

            for a in result:
                tiles[int(a) - 1].click()
            self.driver.find_element_by_id("recaptcha-verify-button").click(); time.sleep(3)
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame(self.driver.find_element_by_xpath("//iframe[@title='recaptcha widget']"))
                if self.driver.find_element_by_id("recaptcha-anchor").get_attribute('aria-checked') == 'true':
                    print("Captcha solved")
                    captcha_solving = False
                else:
                    print("Solve again")
                    captcha_solving = True
            except Exception as err:
                captcha_solving = False
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath("//*[@type='submit']").click()

        # self.driver.switch_to.frame(capcthaframe)
        # print "-------------"
        # print(self.driver.page_source)
        # print "-------------"
        # picturetable = self.driver.find_element_by_class_name('rc-imageselect-challenge')
        # images = []

        # action = webdriver.common.action_chains.ActionChains(self.driver)
        
        # for person in self.driver.find_elements_by_class_name('rc-imageselect-checkbox'):
        #     self.driver.switch_to.default_content()
        #     self.driver.switch_to.frame(capthcaboxframe)
        

        #     action.move_to_element_with_offset(checkbox, 60, 60)
        #     action.click()
        #     action.perform()
       
        #     print "yes"
        #     images.append(person)
 
        # """
        # for row in picturetable.find_elements_by_value(0):
        #     print('row',row)
        #     for col in row.find_elements_by_tag_name('td'):
        #         print('col',col)
        #         images.append(col.find_element_by_tag_name('img'))"""
        # if images == []:
        #     self.fail("Found no captcha images")
        #     return -1
 
        # print("[*] Got answer : " + str(numbers))

        # # checkbox.click()
        # # time.sleep(1)
        # # checkbox.click()
        # # time.sleep(1)

        # for number in numbers:
        #     index = int(number) - 1
            
        #     print('[+] clicked on image '+str(index+1))
        # self.driver.save_screenshot('res.png')
        # verifybutton = self.driver.find_element_by_xpath("//input[@value='Verify']")
        # verifybutton.click()
        # print("[*] Clicked verify button")
        # self.driver.save_screenshot('verify.png')
        # time.sleep(2)
        # """
        # if self.driver.find_element_by_css_selector('.rc-imageselect-incorrect-response').is_displayed() or \
        #                 self.driver.find_element_by_css_selector('.rc-imageselect-error-select-one').is_displayed() or \
        #                 self.driver.find_element_by_css_selector('.rc-imageselect-error-select-more').is_displayed():
        #     self.fail("Incorrect answer from 2captcha")
        #     return -1"""
        # self.driver.switch_to.default_content()
 
        # self.driver.switch_to.frame(capthcaboxframe)
        # """
        # if self.driver.find_element_by_id('recaptcha-anchor').get_attribute('aria-checked') == 'false':
        #     self.fail("Capctha not passed")
        #     return -1"""
        # self.driver.switch_to.default_content()
        # submitbutton = self.driver.find_element_by_xpath("//input[@value='Submit']")
        # submitbutton.click()
        # self.driver.save_screenshot('passed.png')
        # print(self.driver.page_source)
        return 0
 
proxy = None
 
resolver = capcha_resolver(sys.argv[0], proxy)
 
if resolver.get_page() == -1:
    print("[!] Error while getting page")
else:
    print("[+] Opened URL")
 
if resolver.bypass_captcha() == -1:
    print("[!] Error on captcha resolving")
else:
    print("[+] Resolved captcha")
