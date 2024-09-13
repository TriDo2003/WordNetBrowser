import nltk
from backend.WNAdapter import WNAdapter as wa
import streamlit as st

def display_tree(tree, level=0):
    if not tree:
        return
    indent = '&nbsp;' * (level + 2)
    for ss_name, related_ss in tree.items():
        ss = wa.synset(ss_name)
        st.write(f"{indent}={level+2}> {wa.synset_info(ss)}")
        display_tree(related_ss, level + 1)

def main():
    nltk.download('wordnet')

    # Word input
    word = st.text_input("Search for a word",
                        help='Input a word and press Enter (or Return). When entering a multi-part term, use underscores (_) to separate each word. For example: dog, SMILE, Homo_sapiens.')

    # Look up for synsets
    synsets_dict = wa.look_up(word)

    # Print the number of senses
    num_sense = sum([len(synsets_dict[pos]) for pos in synsets_dict.keys()])
    st.write(f"The word '{word}' has **{num_sense}** {'meaning' if num_sense < 2 else 'meanings'}.\n")

    # Create columns
    col1, col2 = st.columns([3, 1]) # Left column 3/4 screen width
    pos_option = [f'{pos} ({len(synsets_dict[pos])})' for pos in synsets_dict.keys() if synsets_dict[pos] != []]
    with col1:
        display_pos_option = {'n': 'noun', 'a': 'adj', 'v': 'verb', 'r': 'adv'}
        pos = st.radio(
            "POS",
            [display_pos_option[s[:1]] + s[1:] for s in pos_option],
            horizontal=True,
            label_visibility='collapsed'
            )
    with col2:
        show_details = st.toggle("Show details", help='Explicitly display the synset ID and inherited attributes of the word relations.')

    if pos == None:
        return
    
    pos = pos[:1]
    
    for i, synset in enumerate(synsets_dict[pos]):
        relations = wa.get_relations(synset, pos)
        
        st.markdown(f"<div style='border: 1px solid black; padding: 10px;'><strong>Sense {i + 1}:</strong> {wa.synset_info(synset)}</div>", unsafe_allow_html=True)

        selected_relation = st.radio(label="Relations", options=['examples'] + list(relations.keys()), horizontal=True, key=f'radio_{i}', label_visibility='collapsed')
        if not selected_relation:
            return
        
        if selected_relation == 'examples':
            st.markdown(wa.synset_examples(synset))
        elif show_details and selected_relation not in wa.CYCLIC_RELATIONS :
            relation_tree = wa.get_relation_recursive(synset, wa.RELATION_NAME_FUNC[pos][selected_relation])
            display_tree(relation_tree)
        else:
            for ss in relations[selected_relation]:
                st.markdown(f' => {wa.synset_info(ss)}')


if __name__ in ['__main__']:
    main()