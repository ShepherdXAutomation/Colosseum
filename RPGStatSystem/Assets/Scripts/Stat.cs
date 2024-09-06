using System.Collections.Generic;
using System;

/// <summary>
/// Generic Stat class which contains every method needed for stats.
/// Type param is used to define which value type is used for the stat (eg. float, int etc.)
/// The value of the stat changes based on the modifications it has applied.
/// It designed to provide functionality to display a variety of things you can do with stats.
/// 
/// eg. adding a temporary health buff or normal stat changes through item changes.
/// </summary>
/// <typeparam name="T"></typeparam>
[Serializable]
public class Stat<T> : IStat<T>
{

    // a list of modifications, for private use only.
    private List<IStatModification<T>> mods;
    // the value of the stat
    private T value;
    // boolean used to check if a stat has been modified or is used the first time.
    private bool isNewOrModified = true;


    #region Constructors

    /// <summary>
    /// Private Constructor used internally to create a new stat and attach the base modification.
    /// </summary>
    /// <param name="id"></param>
    /// <param name="baseModification"></param>
    private Stat(string id, IStatModification baseModification = null)
    {
        mods = new List<IStatModification<T>>();
        this.Id = id;
        if (baseModification != null)
            baseModification.Attach(this);
    }



    /// <summary>
    /// Constructor which should be used to create a new Stat.
    /// Takes in a String for its id, which can be used in game to display the name and a base value of specified type t.
    /// </summary>
    /// <param name="id"></param>
    /// <param name="baseValue"></param>
    public Stat(string id, T baseValue) : this(id, new StatModification<T>(string.Empty, int.MinValue, new Set<T>(), baseValue))
    {
        //this constructor does nothing extra.
    }
    #endregion


    #region important properties and some convenience things

    /// <summary>
    /// Return the Base Modification.
    /// The Base Modification is used for 
    /// </summary>
    public IStatModification<T> BaseMod
    {
        get
        {
            return mods[0];
        }
    }

    public string Id
    {
        get;
        private set;
    }

    public IEnumerable<IStatModification<T>> Modifications
    {
        get
        {
            return mods;
        }
    }

    /// <summary>
    /// Value of the Stat.
    /// Checks first of the stat is new or modified (based on an event) and recalculates the value.
    /// </summary>
    public T Value
    {
        get
        {
            if (isNewOrModified)
            {
                isNewOrModified = false;
                value = default(T);

                foreach (var mod in mods)
                {
                    value = (mod as IStatModification<T>).Accumulate(value);
                }
            }
            return value;
        }
    }
    #endregion

    //modified event
    public event StatModifiedEventHandler modified;

    #region methods
    /// <summary>
    /// Remove a Modifier from the stat
    /// </summary>
    /// <param name="mod"></param>
    internal void RemoveStatMod(IStatModification<T> mod)
    {
        isNewOrModified = true;

        //remove the modifier
        mods.Remove(mod);

        //set the event
        if (modified != null)
        {
            modified(this, new StatModifiedEventArgs<T>(ModificationType.Removed, mod, value, Value));
        }

    }

    /// <summary>
    /// Add a new Modifier to the stat
    /// </summary>
    /// <param name="mod"></param>
    internal void AddStatMod(IStatModification<T> mod)
    {
        isNewOrModified = true;

        //add the new mod
        mods.Add(mod);
        //and sort it
        mods.Sort((a, b) => a.Priority.CompareTo(b.Priority));

        //set the event
        if (modified != null)
        {
            modified(this, new StatModifiedEventArgs<T>(ModificationType.Added, mod, value, Value));
        }
    }

    /// <summary>
    /// fire a event if the stat changed based on the modifier
    /// </summary>
    /// <param name="mod"></param>
    internal void FireStatChanged(IStatModification<T> mod)
    {
        isNewOrModified = true;

        //set the event
        if (modified != null)
        {
            modified(this, new StatModifiedEventArgs<T>(ModificationType.Changed, mod, value, Value));
        }

    }
    #endregion
}
