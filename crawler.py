# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pymongo import MongoClient
import scrapy
import json


class MySpider(scrapy.Spider):
    name = 'MySpider'
    item = []
    file = open('listaProdotti.json','w') # apre in lettura il file dove scrivere il crawler
    connection = MongoClient('mongodb+srv://%s:%s@compr-o-bot-la6cc.mongodb.net' % ("sartoni", "yb8E8Umlq5gKBKp1"))
    connection = connection['shitpost']['shitpost']

    start_urls = [
        'https://shop.app4health.it//',
    ]

    def parse(self, response):
        self.logger.info('A response from %s just arrived!', response.url)

        risultati =  response.selector.xpath('//*[@id="nav"]/ol/li[*]/div/div/div[1]/ul/li[*]/a/@href').extract()
        #risultati= response.css('.level0 .level-top::attr(href)').extract()


        for pagineitems in risultati:

        #LO IGNORA PERCHE DICE CHE E' GIA STATA RICHIESTA
            yield scrapy.Request(pagineitems, callback=self.microCategorie,dont_filter = True)


    def parsedescrizione(self, response):


        tmp_item = { # Please keep all keys lowercase
            "nome" : response.meta.get('nomeProdotto'),
            "link" : response.meta.get('linkProdotto'),
            "macro-categoria" : response.meta.get('macrocategoria').replace('\n', '').replace('\t', '').replace('\r', ''),
            "descrizione" : response.css('.tab-content p::text').extract_first(),
            "immagini" : response.css('#zoom1 > img::attr(src)').extract_first(),
            "prezzo" : response.css('.price::text').extract_first().replace('\xa0','')
        }
      

        self.connection.insert(tmp_item)
        self.item.append(tmp_item) # Appende alla lista l'item appena creato


    # ======= CALLBACK ESEGUITA PER OGNI MACRO-CATEGORIA ==========
    def microCategorie(self, response):
        for i in range(1,3):
            urlcategory = response.url
            # SELECTOR DIRETTO h1[class=category-title]::text
            macrocategoria = urlcategory.replace('https://shop.app4health.it/','')


            ScansioneProdotti = response.url + "?p=" + str(i)
            self.logger.info('A response from %s just arrived!', response.url)

            yield scrapy.Request(ScansioneProdotti, callback=self.prodotti,dont_filter = True,
                                 meta={'macrocategoria': macrocategoria } ) # Passa alla callback un parametro


    def prodotti(self, response):
        print (response.url + " PAGINE PRODOTTI DA ITERARE")
        linkProdotto = response.xpath('//*[@id="top"]/body/div[2]/div/div/div[4]/div/div[2]/div[4]/ul/li[*]/div/div/h2[2]/a/@href').extract()
        nomeProdotto = response.xpath('//*[@id="top"]/body/div[2]/div/div/div[4]/div/div[2]/div[4]/ul/li[*]/div/div/h2[2]/a/@title').extract()
        print ( nomeProdotto ) # Printa una lista di pdodotti

	    # TODO: visitare qua il link di ogni prodotto ed aggiungere descrizione 
        for i in range(0, len(linkProdotto)):
            yield scrapy.Request(linkProdotto[i], callback = self.parsedescrizione, dont_filter = True,
                                 meta={'macrocategoria': response.meta.get('macrocategoria'),
                                       'linkProdotto': linkProdotto[i],
                                       'nomeProdotto': nomeProdotto[i],
                                      }) # Passa la macrocategoria


    def __del__(self):
        self.file.write(json.dumps(self.item))
        self.file.close()
