const Attempts = require('../models/attempts');
const Tests = require('../models/test');

const attemptedTest = async (req, res) => {
    const { email, testCode } = req.query;

    try {
        const test = await Tests.find({test_code : testCode});
        console.log(test);
        if(test.length === 0){
            return res.json({msg:"Test not found"});
        }
        const result = await Attempts.find({ email, 'tests.testCode': testCode }).exec();
        return res.status(200).json(result);
    } catch (err) {
        console.error("Error finding attempt:", err);
        return res.status(404).json({ err });
    }
};


const addAttempt = async (req,res) => {
    const email = req.query.email;
    const testCode = req.query.testCode;
    try {
        const result = await Attempts.updateOne(
            { email: email },
            { $push: { tests: { testCode: testCode } } },
            { upsert: true } // This will create a new document if the email doesn't exist
        );
        console.log('Update result:', result);
        res.status(201).json(result);
    } catch (error) {
        console.error('Error updating document:', error);
        res.json(error);
    }

}

const deleteAttempt = async () => {
    try {
        const result = await Attempts.deleteMany({});
        console.log('All documents deleted:', result);
    } catch (error) {
        console.error('Error deleting documents:', error);
    }
};

const addWarning = async (req, res) => {
    const { email, testCode, warningType } = req.body;

    try {
        // Find the document with the specified email and testCode
        const attempt = await Attempts.findOne({ email, 'tests.testCode': testCode });

        if (attempt) {
            let test = attempt.tests.find(test => test.testCode === testCode);

            if (test) {
                let warning = test.warnings.find(warning => warning.warningType === warningType);

                if (warning) {
                    // Increment warningCount if the warningType exists
                    warning.warningCount += 1;
                } else {
                    // Add new warning if the warningType does not exist
                    test.warnings.push({ warningType, warningCount: 1 });
                }

                await attempt.save();
                res.status(200).json({ message: 'Warning count updated', attempt });
            } else {
                res.status(404).json({ message: 'Test not found' });
            }
        } else {
            res.status(404).json({ message: 'Attempt not found' });
        }
    } catch (error) {
        res.status(500).json({ message: 'Error updating warning count', error });
    }
}

const getWarnings = async (req, res) => {
    const { email, testCode } = req.query;
    try {
        const attempt = await Attempts.findOne({ email, 'tests.testCode': testCode });

        if (attempt) {
            // Find the specific test with the testCode
            const test = attempt.tests.find(test => test.testCode === testCode);

            if (test) {
                res.status(200).json({ warnings: test.warnings });
            } else {
                res.status(404).json({ message: 'Test not found' });
            }
        } else {
            res.status(404).json({ message: 'Attempt not found' });
        }
    } catch (error) {
        res.status(500).json({ message: "Attempt not found"});
    }
}

const attempts = async (req, res) => {
    const { email } = req.query;

    try {        
        const result = await Attempts.find({ email}).exec();
        return res.status(200).json(result);
    } catch (err) {
        console.error("Error finding attempt:", err);
        return res.status(404).json({ err });
    }
};

const getAllWarnings = async (req, res) => {
    const { testCode } = req.query;

    try {
        const warnings = await Attempts.aggregate([
            { $unwind: '$tests' },
            { $match: { 'tests.testCode': testCode } },
            {
                $project: {
                    email: 1,
                    warnings: '$tests.warnings'
                }
            }
        ]);

        res.status(200).json({ warnings });
    } catch (err) {
        console.error("Error fetching warnings for all students:", err);
        res.status(500).json({ error: 'Server error' });
    }
};






module.exports = {
    attemptedTest,
    addAttempt,
    deleteAttempt,
    addWarning,
    getWarnings,
    attempts,
    getAllWarnings
}