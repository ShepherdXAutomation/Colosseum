using UnityEngine;
using System.Collections;

public class Hero : MonoBehaviour {

    public Stat<int> vitality;
    public Stat<int> strength;
    public Stat<int> health;
    public Stat<float> critChance;
    public Stat<float> critDmg;


	// Use this for initialization
	void Start () {
        vitality = new Stat<int>("Vitality", 70);
        strength = new Stat<int>("Strength", 70);
        health = new Stat<int>("Health", vitality.Value * 50);
        critChance = new Stat<float>("Critical Hit Chance", 5f);
        critDmg = new Stat<float>("Critical Hit Damage", 50f);
    }
	
	// Update is called once per frame
	void Update () {
	
	}

    public void Test()
    {
        vitality.BaseMod.Value -= 10;

        vitality.modified += OnVitalityChanged;

        StatModification<int> bonus = new StatModification<int>("Bonus", 1, new AddInt(), 50);
        vitality.AddStatMod(bonus);
        vitality.RemoveStatMod(bonus);
    }

    private void OnVitalityChanged(object sender, StatModifiedEventArgs e)
    {
        var args = (StatModifiedEventArgs<int>)e; // need to cast the arguments parameter to your need
        health.BaseMod.Value = args.newValue * 10;
    }

}
