import pandas as pd
import requests
import json
import streamlit as st

API_KEY = st.secrets['API_KEY']
PROJECT = 'all'
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"


def id_plant(img_data,organ = 'leaf'):
    files = [
            ('images', ('img',img_data))
            ]
    req = requests.Request('POST', url = api_endpoint, files = files, data = {'organs': [organ,]})
    prepared = req.prepare()
    s = requests.Session()
    response = s.send(prepared)
    result = json.loads(response.text)
    return result['bestMatch'], result['results'][0]['species']['commonNames'], result['results'][0]['score']

def species_id(plant_id):
    species = plant_id[0].lower().split()
    common = plant_id[1]
    likelihood = plant_id[2]
    return ''.join(species[0] + ' ' + species[1]), common, likelihood

def is_invasive(species_id,invasives):
    if species_id in invasives['Scientific Name'].str.lower().to_list():
        if not pd.isnull(invasives[invasives['Scientif Name'].str.lower()==species_id]['Link']):
            factsheet = link
            return 'Invasive', link
        else:
            return 'Invasive', None
    else:
        return 'Non-invasive', None
    
@st.cache_data
def load_invasives():
    invasives = pd.read_csv('./data/pa_invasives.csv')
    return invasives
    
if __name__ == '__main__':
    st.title('PA Invasives')
    st.set_page_config(layout='wide')
    info, classifier = st.columns(2)
    with info:
        st.header('Is it invasive?')
        st.subheader('What is an invasive plant?')
        st.markdown(
    '''Invasive plants are those that:          
    * Are **not native** to an area
    * **Spread** quickly
    * Cause **economic or environmental harm**, or harm to human health.''')
        
        st.write("Invasive plants have been brought into areas, and this can happen accidentally or on purpose. They are often referred to as “exotic,” “alien,” “introduced,” or “non-native” species.")


        st.write("In their natural range, these plants are limited by factors that keep them in balance including pests, herbivores, or diseases. However, when introduced into an area where **these limitations are absent**, some species can become invasive.",type = str)

        st.subheader('Why should I care about invasive plants?')
        st.write('''Invasive plants **reduce habitat for native wildlife**. Invasive plants out-compete natives and “take over” native plants' habitats.''')

        st.write("They often emerge earlier in the spring and push natives out through fast reproduction. This limits habitat available for native wildlife and disrupts the food chain.")


        st.write("Invasives also cost money. According to the U.S. Fish and Wildlife Service (PDF)Opens In A New Window, the U.S. spends **more than $120 billion on invasive species each year**.", type = str)

        st.subheader('Who determines if a plant is invasive?')
        st.write('The PA DCNR maintains a list of invasive plant species. [Click here](https://elibrary.dcnr.pa.gov/GetDocument?docId=2700788&DocName=dcnr_20033786.pdf) for a full list of invasive plant species and [here](https://www.pa.gov/agencies/dcnr/conservation/wild-plants/invasive-plants/invasive-plant-fact-sheets) for a list of invasive plant fact sheets.')
    
    with classifier:
        invasives = load_invasives()
        st.subheader('Is this plant invasive?')
        st.write('''Upload a clear image of a plant below to determine if it is likely invasive or not. The classifier works best if you include only a single plant in your image,
                and make sure to capture any distinctive features like leaf shape, fruit, or flowers.
                
                You may upload more than one image at a time.''')
        with st.form(key = 'img_submit'):
            imgs = st.file_uploader(label = 'Upload plant image here (jpg or png)', type = ['png','jpg'],accept_multiple_files=True)
            submit = st.form_submit_button(label = 'Submit')
        if submit:
            if imgs is None:
                st.write('No file uploaded -- upload a picture of a plant!')
            else:
                for img in imgs:
                    st.image(img)
                    plant_id = id_plant(img)
                    species, common, likelihood = species_id(plant_id)
                    invasive, factsheet = is_invasive(species,invasives)
                    if factsheet:
                        st.write(f"This plant is likely *{species}* (confidence {likelihood*100:.1f}\%, common names **{common}**).\n #### It is **{invasive}** in Pennsylvania. Learn more [here]({factsheet}).")
                    else:
                        st.write(f"This plant is likely *{species}* (confidence {likelihood*100:.1f}\%, common names **{common}**).\n #### It is **{invasive}** in Pennsylvania.")

