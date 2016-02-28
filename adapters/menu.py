def show_menu(items, start=0, prompt="Please select: ", sort=True, location=False):
    if (sort):
        items = sorted(items)
    items.append("Exit")
    while True:
        for idx,option in enumerate(items):
            print (str(idx+start)+" "+str(option))
        selection=raw_input(prompt)
        try:
            selection=int(selection)
            if (selection < 0):
                raise
            if (not location):
                return items[selection-start]
            else:
                return selection
        except:
            if selection.lower() == 'q':
                return(len(items))
            print ("Unknown Option Selected!")
