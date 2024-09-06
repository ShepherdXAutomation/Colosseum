using UnityEngine;
using System.Collections;
using System;

[Serializable]
public class StatModification<T> : IStatModification<T>
{
    private T value;
    private IAccumulator<T> accumulator;

    public StatModification(string id, int priority, IAccumulator<T> accumulator, T value)
    {
        this.Id = id;
        this.Priority = priority;
        this.accumulator = accumulator;
        this.Value = value;
    }

    public string Id { get; private set; }

    public int Priority { get; private set; }

    public event ModificationModifiedEventHandler Modified;
    public event ModificationModifiedEventHandler modified;

    public IStat Assignee { get; private set; }

    public T Value
    {
        get
        {
            return value;
        }
        set
        {
            if (object.Equals(this.value, value))
                return;
            var oldValue = this.value;
            this.value = value;
            if (Assignee != null)
                (Assignee as Stat<T>).FireStatChanged(this);
            if (Modified != null)
                Modified(this, new ModificationModifiedEventArgs<T>(ModificationType.Changed, Assignee, oldValue, value));
        }
    }

    public void Attach(IStat stat)
    {
        if (Assignee != null)
            return;

        Assignee = stat;

        (Assignee as Stat<T>).AddStatMod(this);
        if (Modified != null)
            Modified(this, new ModificationModifiedEventArgs<T>(ModificationType.Added, stat, value, value));
    }

    public void Detach()
    {
        if (Assignee == null)
            return;

        var oldAssignee = Assignee;
        Assignee = null;
        (oldAssignee as Stat<T>).RemoveStatMod(this);
        if (Modified != null)
        {
            Modified(this, new ModificationModifiedEventArgs<T>(ModificationType.Removed, oldAssignee, value, value));
        }
    }

    public T Accumulate(T currentValue)
    {
        return accumulator.Accumulate(currentValue, value);
    }
}
