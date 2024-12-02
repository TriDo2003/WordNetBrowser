import streamlit as st
from backend.WNAdapter import WNAdapter as wa
import backend.LCH as utils
#import nltk


def main():
    #nltk.data.path.append('../wndb')

    input = st.text_input("Search for the Lowest Common Hyponym for a list of words", help='"table, chair, sofa" -> "furniture"')
    words = utils.parse_input(input)

    st.write(f"Entered {len(words)} words: {words}")

    if len(words) < 2:
        st.write("Please enter at least 2 words!")
        return
    

    lch, can = utils.lowest_common_hypernyms(words, lambda ss1, ss2: ss1.shortest_path_distance(ss2))
    paths = utils.visualize_lch(lch, can)

    for pos in lch.keys():
        st.markdown(f"##### The meaning you are referring to:")
        for ss in can[pos]:
            st.markdown(f"- *{wa.synset_info(ss)}*")

        ss = lch[pos][0]
        st.markdown(f"##### Lowest Common Hypernym: <span style='color:red'>{ss.name()}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='border: 1px solid black; padding: 10px;'><strong>{pos}:</strong> {wa.synset_info(ss)}</div>", unsafe_allow_html=True)

        st.graphviz_chart(paths[pos].source)
        st.markdown('---')

if __name__ in ['__main__']:
    main()
