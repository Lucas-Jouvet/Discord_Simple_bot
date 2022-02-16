import discord
import os
import time

class POP(discord.Client):

    tab_chanel = []     #Tableau contenant les différents channels
    dico_message = {}   #Dictionnaire ayant pour clé le channel, et un tableau de messages lié au channel

    async def on_ready(self):
        t,d = self.fichier_config_read() #Récupérations du tableau, et du dictionnaire
        if t != []: #Initialisation du tableau et du dictionnaire
            self.init_tab_channel(t)
            self.init_dico(d)
        print('Bot OK')

    #Fonction asynchrone permettant de gérer les différentes commandes :
    #   !!help                                  : Permet à l'utilisateur de voir les différentes commandes disponibles
    #   !!add #CHANNEL [message1,message2,...]  : Ajoute des messages dans la file de messages.
    #   !!del #CHANNEL [message1,message2,...]  : Supprime des messages dans la file de messages.
    #   !!liste #CHANNEL                        : Liste les messages de la file en lien avec le channel.
    #   !!go_chart #CHANNEL                     : Exécute la file de messages du channel en argument.
    #   !!go_chart                              : Exécute la file de messages de l'ensemble des channels.
    async def on_message(self, message):
        #Pour éviter que le bot se réponde à lui-même et donc faire des boucles sur lui-même
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!!help'):
            await message.channel.send("!!add #CHANNEL [message1,message2,...] : Ajoute des messages dans la file de messages.\n\n"
                                       "!!del #CHANNEL [message1,message2,...] : Supprime des messages dans la file de messages.\n\n"
                                       "!!liste #CHANNEL : Liste les messages de la file en lien avec le channel.\n\n"
                                       "!!go_chart #CHANNEL : Exécute la file de messages du channel en argument.\n\n"
                                       "!!go_chart : Exécute la file de messages de l'ensemble des channels.")

        if message.content.startswith('!!liste'):
            tab_m = message.content.split()
            #Récupération de l'id du channel
            id = tab_m[1]
            id = id.split('#')[1].split('>')[0]
            try:
                #Vérification que le channel soit correct
                id = int(id)
                if id in self.dico_message:
                    #Récupération de messages
                    tab = self.dico_message.get(id)
                    #Mise en forme du message à retourner
                    mess = "liste des messages pour "+message.content.split()[1]+" :\n"
                    for x in tab:
                        mess = mess +""+str(x)+"\n"
                    #Envoi du message
                    await message.channel.send(mess)
                else :
                    await message.channel.send("Ce channel n'existe pas")
            except ValueError:
                await message.channel.send("Ce channel n'existe pas")

        if message.content.startswith('!!go_chart'):
            #Dans cette partie la fonction sleep est utilisée pour éviter de surcharger les autres bots
            b_id = False
            tab_m = message.content.split()
            #Si un channel est précisé exécution des messages pour le channel mentionné
            if len(tab_m ) > 1:
                id = tab_m[1]
                id = id.split('#')[1].split('>')[0]
                try:
                    id = int(id)
                    if id in self.dico_message:
                        tab = self.dico_message.get(id)
                        for m in tab:
                            c = client.get_channel(int(id))
                            await c.send(m)
                            time.sleep(10)
                        b_id = True
                except ValueError:
                    b_id = False
            else:
                b_id = False
            #Si aucun channel n'est précisé exécution de l'ensemble des messages
            if b_id == False:
                for id in self.tab_chanel:
                    if id in self.dico_message:
                        tab = self.dico_message.get(id)
                        for m in tab:
                            c = client.get_channel(int(id))
                            await c.send(m)
                            time.sleep(10)
                        time.sleep(10)


        if message.content.startswith('!!del'):
            tab_m = message.content.split()
            id = tab_m[1]
            id = id.split('#')[1].split('>')[0]
            tab_m = message.content.split('[')
            if len(tab_m) > 1:
                tab_m = tab_m[1]
                tab_m = tab_m.split(']')[0]
                tab_m = tab_m.split(',')
                if int(id) in self.dico_message:
                    tab = self.dico_message.get(int(id))
                    for x in tab_m:
                        if x in tab:
                            tab.pop(tab.index(x))
                    if tab == []:
                        self.dico_message.pop(int(id))
                        self.tab_chanel.pop(self.tab_chanel.index(int(id)))
                    else:
                        self.dico_message.update({int(id):tab})
                    self.fichier_config_write(self.tab_chanel, self.get_tab_dico())





        if message.content.startswith('!!add '):
            tab_m = message.content.split()
            id = tab_m[1]
            id = id.split('#')[1].split('>')[0]
            tab_m = message.content.split('[')
            if len(tab_m) > 1:
                tab_m = tab_m[1]
                tab_m = tab_m.split(']')[0]
                tab_m =tab_m.split(',')
                try:
                    id =int(id)
                    if client.get_channel(id):
                        if not(id in self.tab_chanel):
                            self.tab_chanel.append(id)
                            tab = []
                        else:
                            tab = self.dico_message.get(id)
                        tab = tab + tab_m
                        self.dico_message.update({id:tab})
                        self.fichier_config_write(self.tab_chanel, self.get_tab_dico())
                except ValueError:
                    await message.channel.send("Ce channel n'existe pas")


    def init_tab_channel(self,tab):
        for x in tab:
            if x != "\n":
                x = x.split("\n")[0]
                self.tab_chanel.append(int(x))

    def init_dico(self,tab_dico):
        for x in tab_dico:
            tmp = x.split(":")
            id = tmp[0]
            if len(tmp) > 1:
                messages = tmp[1].split("\n")
                messages = messages[0].split(",")
                self.dico_message.update({int(id):messages[1:]})

            else:
                self.dico_message.update({id: []})

    def get_tab_dico(self):
        messages = []
        for cle,valeur in self.dico_message.items():
            m = str(cle)+":"
            if len(valeur) > 0:
                for i in valeur:
                    m = m+","
                    m = m+i
            messages.append(m)
        return messages


    def bis_fichier_config_read(self,fichier):
        r = []
        try:
            file = open(fichier, "r")
            for line in file:
                r.append(str(line))
            file.close()

        except IOError:
            print("Erreur lors de l'ouverture du fichier")
        return r

    def fichier_config_read(self):
        return self.bis_fichier_config_read('conf_channels.bot'),self.bis_fichier_config_read('conf_messages.bot')

    def bis_fichier_config_write(self,fichier,infos):
        try:
            file = open(fichier, "r")
            file.close()
            os.remove(fichier)
        except IOError:
            print("création du fichier conf pour " + 'conf.bot')

        try:
            file = open(fichier, "a", encoding="utf-8")
            for f in infos:
                try:
                    # print(f)
                    file.write(str(f)+"\n")
                except IOError:
                    print("Prblème d'écriture : " + f)
            file.close()
        except IOError:
            print("Impossible d'ouvrir le fichier de config " + fichier)

    def fichier_config_write(self, channels,messages):
        self.bis_fichier_config_write('conf_channels.bot', channels)
        self.bis_fichier_config_write('conf_messages.bot', messages)

client = POP()
client.run('TOKEN')#Token de connexion à discord
