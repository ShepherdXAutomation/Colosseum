# RPGStatSystem
A simple but flexible RPG Stat System


## Samples

Create a new stat:

    Stat<int> vitality = new Stat<int>("Vitality", 50) // second param is the base value

Retrieve stat value:

    Console.WriteLine("Value for stat: " + vitality.Id + " = " + vitality.Value); // or Debug.Log(); etc.

Change the value:

    vitality.BaseMod.Value += 10; // other operations work the same.

You can also do recalculations or something on modification of stats (Sample -> Recalulate Health on Vitality Change):

    Stat<int> health = new Stat<int>("Health", vitality.Value * 10);
    vitality.modified += (sender, arguments) => {
      var args = (StatModifiedEventArgs<int>) arguments; // need to cast the arguments parameter to your need
      health.BaseMod.Value = args.newValue * 10;
    };
	
	//or:
	 vitality.modified += OnVitalityChanged;
	 private void OnVitalityChanged(object sender, StatModifiedEventArgs e)
    {
        var args = (StatModifiedEventArgs<int>)e; // need to cast the arguments parameter to your need
        health.BaseMod.Value = args.newValue * 10;
    }
	
      
Adding and removing a modification:

    StatModification<int> bonus = new StatModification<int>("Bonus", 1, new AddInt(), 50);
    vitality.AddStatMod(bonus);
    vitality.RemoveStatMod(bonus);
It is important to note that you can only add int mods on int stats and float mods on float stats.


to be extended
